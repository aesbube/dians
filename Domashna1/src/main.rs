use chrono::{Local, NaiveDate};
use futures::future::join_all;
use reqwest::Client;
use scraper::{Html, Selector};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Write};
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
    let mut data_all: HashMap<String, Value> = load_data().unwrap_or_default();
    let sellers = get_sellers(&client).await?;

    if data_all.is_empty() {
        let futures: Vec<_> = sellers
            .iter()
            .map(|seller| scrape_seller_data(seller.clone(), &client, &data_all))
            .collect();

        let results = join_all(futures).await;

        for result in results {
            if let Ok((seller, data)) = result {
                data_all.insert(seller, json!(data));
            }
        }
    } else {
        for seller in &sellers {
            if data_all.contains_key(seller) {
                if let Err(e) = update_seller_data(seller, &client, &mut data_all).await {
                    eprintln!("Error updating {}: {}", seller, e);
                }
            } else {
                if let Ok((seller_name, data)) =
                    scrape_seller_data(seller.clone(), &client, &data_all).await
                {
                    data_all.insert(seller_name, json!(data));
                }
            }
        }
    }

    save_data(&data_all)?;

    println!(
        "It took {:.3} seconds to scrape the data",
        start.elapsed().as_secs_f64()
    );

    Ok(())
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

async fn scrape_seller_data(
    seller: String,
    client: &Client,
    data_all: &HashMap<String, Value>,
) -> Result<(String, Vec<StockData>), Box<dyn std::error::Error>> {
    if !data_all.contains_key(&seller)
        || (data_all
            .get(&seller)
            .and_then(|v| v.as_array())
            .map_or(true, |arr| arr.is_empty()))
    {
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
    } else {
        Ok((seller, Vec::new()))
    }
}

async fn update_seller_data(
    seller: &str,
    client: &Client,
    data_all: &mut HashMap<String, Value>,
) -> Result<(), Box<dyn std::error::Error>> {
    let seller_data = match data_all.get(seller) {
        Some(data) => data,
        None => {
            println!("No data found for seller {}, scraping new data", seller);
            let (_, new_data) = scrape_seller_data(seller.to_string(), client, data_all).await?;
            if !new_data.is_empty() {
                data_all.insert(seller.to_string(), json!(new_data));
            }
            return Ok(());
        }
    };

    let from_date = match seller_data {
        Value::Array(arr) => {
            if arr.is_empty() {
                println!("Empty data found for seller {}, scraping new data", seller);
                let (_, new_data) =
                    scrape_seller_data(seller.to_string(), client, data_all).await?;
                if !new_data.is_empty() {
                    data_all.insert(seller.to_string(), json!(new_data));
                }
                return Ok(());
            }

            if let Some(first_entry) = arr.first() {
                let date_str = first_entry
                    .get("date")
                    .and_then(|d| d.as_str())
                    .ok_or("Invalid date format")?;
                NaiveDate::parse_from_str(date_str, "%d.%m.%Y")? + chrono::Duration::days(1)
            } else {
                return Ok(());
            }
        }
        Value::String(date_str) => NaiveDate::parse_from_str(date_str, "%Y-%m-%d")?,
        _ => {
            println!(
                "Invalid data format for seller {}, scraping new data",
                seller
            );
            let (_, new_data) = scrape_seller_data(seller.to_string(), client, data_all).await?;
            if !new_data.is_empty() {
                data_all.insert(seller.to_string(), json!(new_data));
            }
            return Ok(());
        }
    };

    let mut to_date = from_date - chrono::Duration::days(1);
    let today = Local::now().naive_local().date();
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
        match seller_data {
            Value::Array(existing_data) => {
                let mut combined_data = new_data;
                combined_data.extend(
                    existing_data
                        .iter()
                        .filter_map(|v| serde_json::from_value::<StockData>(v.clone()).ok()),
                );
                data_all.insert(seller.to_string(), json!(combined_data));
            }
            _ => {
                data_all.insert(seller.to_string(), json!(new_data));
            }
        }
    }

    Ok(())
}

fn load_data() -> Result<HashMap<String, Value>, Box<dyn std::error::Error>> {
    let mut file = File::open("scraped_data.json")?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(serde_json::from_str(&contents)?)
}

fn save_data(data: &HashMap<String, Value>) -> Result<(), Box<dyn std::error::Error>> {
    let mut file = File::create("scraped_data.json")?;
    file.write_all(serde_json::to_string_pretty(data)?.as_bytes())?;
    Ok(())
}
