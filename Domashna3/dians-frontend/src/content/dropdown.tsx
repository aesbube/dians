import React, { useEffect, useState } from 'react';
import { Theme, useTheme } from '@mui/material/styles';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import axios from 'axios';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

function getStyles(name: string, selectedOptions: string[], theme: Theme) {
  return {
    fontWeight: selectedOptions.includes(name)
      ? theme.typography.fontWeightMedium
      : theme.typography.fontWeightRegular,
  };
}

export default function Dropdown() {
  const theme = useTheme();
  const [options, setOptions] = useState<string[]>([]);
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);

  useEffect(() => {
    // Fetch dropdown options from the API
    axios
      .get('http://localhost:8000/stocks')
      .then((response) => {
        console.log("Fetched options:", response); 
        setOptions(response.data);
      })
      .catch((error) => console.error("Error fetching dropdown options:", error));
  }, []);

  const handleChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value as string[]; 
    setSelectedOptions(value);
  };

  return (
    <div>
      <FormControl sx={{ m: 1, width: 300 }}>
        <InputLabel id="dropdown-label">Name</InputLabel>
        <Select
          labelId="dropdown-label"
          id="dropdown"
          multiple
          value={selectedOptions}
          onChange={handleChange}
          input={<OutlinedInput label="Name" />}
          MenuProps={MenuProps}
        >
          {options.map((name) => (
            <MenuItem
              key={name}
              value={name}
              style={getStyles(name, selectedOptions, theme)}
            >
              {name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );
}
