import React from "react";
import { Theme, useTheme } from "@mui/material/styles";
import OutlinedInput from "@mui/material/OutlinedInput";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select, { SelectChangeEvent } from "@mui/material/Select";

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

function getStyles(
  name: string,
  selectedOption: string | undefined,
  theme: Theme
) {
  return {
    fontWeight:
      selectedOption === name
        ? theme.typography.fontWeightMedium
        : theme.typography.fontWeightRegular,
  };
}

interface DropdownProps {
  options: string[];
  selectedStock: string;
  onSelectionChange: (selectedOption: string) => void;
}

const Dropdown: React.FC<DropdownProps> = ({
  options,
  selectedStock,
  onSelectionChange,
}) => {
  const theme = useTheme();

  const handleChange = (event: SelectChangeEvent<string>) => {
    onSelectionChange(event.target.value as string);
  };

  return (
    <div>
      <FormControl
        sx={{
          m: 1,
          width: 300,
          "& .MuiOutlinedInput-root": {
            "& fieldset": {
              borderColor: "lightgray", 
            },
          },
          "& .MuiInputLabel-root": {
            color: "lightgray", 
          },
        }}
      >
        <InputLabel id="dropdown-label">Name</InputLabel>
        <Select
          labelId="dropdown-label"
          id="dropdown"
          value={selectedStock || ""}
          onChange={handleChange}
          input={<OutlinedInput label="Name" />}
          MenuProps={MenuProps}
          sx={{ color: "lightgray" }}
        >
          {options.map((name) => (
            <MenuItem
              key={name}
              value={name}
              style={getStyles(name, selectedStock, theme)
              }
            >
              {name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );
};

export default Dropdown;
