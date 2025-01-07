use chrono::{Local, NaiveDate};
use mongodb::{
    bson::{doc, to_bson, Document},
    options::ClientOptions,
    Client as MongoClient,
};
use reqwest::Client;
use scraper::{Html, Selector};
use serde::{Deserialize, Serialize};
use std::time::Instant;

#[derive(Debug, Serialize, Deserialize, Clone)]
struct StockData {
    date: String,
    last_transaction: String,
    max_value: String,
    min_value: String,
    average: String,
    change: String,
    volume: String,
    best_sales: String,
    all_sales: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let start = Instant::now();
    let client = Client::new();

    dotenv::from_path("../.env").ok();
    
    let mongo_uri = env::var("MONGO_URI").unwrap_or_else(|_| "mongodb://localhost:27017".to_string());
    let mongo_client = connect_to_mongodb(&mongo_uri).await?;
    let db = mongo_client.database("stock_data");
    let collection = db.collection::<Document>("stock_records");

    let sellers = get_sellers(&client).await?;

    for seller in &sellers {
        if let Ok(Some(_)) = collection.find_one(doc! { "_id": seller }, None).await {
            if let Err(e) = update_seller_data(seller, &client, &collection).await {
                eprintln!("Error updating {}: {}", seller, e);
            }
        } else {
            if let Ok((_, data)) = scrape_seller_data(seller.clone(), &client).await {
                save_to_mongodb(&collection, seller, &data).await?;
            }
        }
    }

    println!(
        "It took {:.3} seconds to scrape the data",
        start.elapsed().as_secs_f64()
    );

    Ok(())
}

async fn connect_to_mongodb(uri: &str) -> Result<MongoClient, mongodb::error::Error> {
    let client_options = ClientOptions::parse(uri).await?;
    MongoClient::with_options(client_options)
}

async fn save_to_mongodb(
    collection: &mongodb::Collection<Document>,
    seller: &str,
    data: &[StockData],
) -> Result<(), Box<dyn std::error::Error>> {
    let data_bson = to_bson(data)?;
    
    let update = doc! {
        "$set": {
            "_id": seller,
            "data": data_bson
        }
    };

    collection
        .update_one(
            doc! { "_id": seller },
            update,
            mongodb::options::UpdateOptions::builder().upsert(true).build(),
        )
        .await?;

    Ok(())
}

async fn get_last_date(
    collection: &mongodb::Collection<Document>,
    seller: &str,
) -> Result<Option<NaiveDate>, Box<dyn std::error::Error>> {
    if let Some(doc) = collection.find_one(doc! { "_id": seller }, None).await? {
        if let Some(data) = doc.get_array("data").ok() {
            if let Some(first_item) = data.first() {
                if let Some(date_str) = first_item.as_document().and_then(|d| d.get_str("date").ok()) {
                    return Ok(Some(NaiveDate::parse_from_str(date_str, "%d.%m.%Y")?));
                }
            }
        }
    }
    Ok(None)
}

async fn update_seller_data(
    seller: &str,
    client: &Client,
    collection: &mongodb::Collection<Document>,
) -> Result<(), Box<dyn std::error::Error>> {
    let last_date = match get_last_date(collection, seller).await? {
        Some(date) => date,
        None => {
            let (_, new_data) = scrape_seller_data(seller.to_string(), client).await?;
            save_to_mongodb(collection, seller, &new_data).await?;
            return Ok(());
        }
    };

    let mut to_date = last_date;
    let today: NaiveDate = Local::now().naive_local().date();
    let mut new_data = Vec::new();
    println!("Now updating seller {}", seller);

    while to_date <= today {
        let from = std::cmp::min(to_date + chrono::Duration::days(1), today);
        to_date = from + chrono::Duration::days(365);

        match scrape_page(seller, from, to_date, client).await {
            Ok(mut page_data) => new_data.append(&mut page_data),
            Err(_) => continue,
        }
    }

    if !new_data.is_empty() {
        let existing_doc = collection.find_one(doc! { "_id": seller }, None).await?;
        if let Some(doc) = existing_doc {
            if let Ok(mut existing_data) = doc.get_array("data").map(|arr| {
                arr.iter()
                    .filter_map(|item| {
                        if let Ok(stock_data) = mongodb::bson::from_bson::<StockData>(item.clone()) {
                            Some(stock_data)
                        } else {
                            None
                        }
                    })
                    .collect::<Vec<StockData>>()
            }) {
                new_data.append(&mut existing_data);
            }
        }
        
        save_to_mongodb(collection, seller, &new_data).await?;
    }

    Ok(())
}

async fn scrape_seller_data(
    seller: String,
    client: &Client,
) -> Result<(String, Vec<StockData>), Box<dyn std::error::Error>> {
    println!("Now scraping for seller {}", seller);
    let mut data = Vec::new();
    let mut to_date = Local::now().naive_local().date() + chrono::Duration::days(366);

    for _ in 0..10 {
        to_date -= chrono::Duration::days(366);
        let from_date = to_date - chrono::Duration::days(365);
        match scrape_page(&seller, from_date, to_date, client).await {
            Ok(mut page_data) => data.append(&mut page_data),
            Err(_) => continue,
        }
    }

    Ok((seller, data))
}

async fn scrape_page(
    seller: &str,
    from_date: NaiveDate,
    to_date: NaiveDate,
    client: &Client,
) -> Result<Vec<StockData>, Box<dyn std::error::Error>> {
    let url = format!(
        "https://www.mse.mk/mk/stats/symbolhistory/{}/?FromDate={}&ToDate={}",
        seller,
        from_date.format("%Y-%m-%d"),
        to_date.format("%Y-%m-%d")
    );

    let response = client.get(&url).send().await?.text().await?;
    let document = Html::parse_document(&response);
    let row_selector = Selector::parse("tbody tr").unwrap();
    let cell_selector = Selector::parse("td").unwrap();

    let mut data = Vec::new();

    for row in document.select(&row_selector) {
        let cells: Vec<String> = row
            .select(&cell_selector)
            .map(|cell| cell.text().collect::<String>().trim().to_string())
            .collect();

        if cells.len() >= 9 && !cells[2].is_empty() {
            let date = NaiveDate::parse_from_str(&cells[0], "%d.%m.%Y")?;
            data.push(StockData {
                date: date.format("%d.%m.%Y").to_string(),
                last_transaction: format!("{} ден.", cells[1].clone()),
                max_value: format!("{} ден.", cells[2].clone()),
                min_value: format!("{} ден.", cells[3].clone()),
                average: format!("{} ден.", cells[4].clone()),
                change: cells[5].clone(),
                volume: cells[6].clone(),
                best_sales: format!("{} ден.", cells[7].clone()),
                all_sales: format!("{} ден.", cells[8].clone()),
            });
        }
    }

    Ok(data)
}

async fn get_sellers(client: &Client) -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let url = "https://www.mse.mk/mk/stats/symbolhistory/ADIN";
    let response = client.get(url).send().await?.text().await?;
    let document = Html::parse_document(&response);
    let selector = Selector::parse("option").unwrap();

    let sellers: Vec<String> = document
        .select(&selector)
        .filter_map(|element| {
            let text = element.text().collect::<String>();
            if !text.chars().any(|c| c.is_numeric()) {
                Some(text)
            } else {
                None
            }
        })
        .collect();

    Ok(sellers)
}