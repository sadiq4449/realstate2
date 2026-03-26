import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/** Listing document from API. */
export interface Property {
  id: string;
  owner_id?: string;
  title: string;
  city: string;
  rent_monthly: number;
  bedrooms: number;
  bathrooms: number;
  furnished: boolean;
  amenities: string[];
  images: string[];
  description?: string;
  address?: string;
  status?: string;
  location?: { type: string; coordinates: number[] };
}

interface PropertiesState {
  searchResults: Property[];
  searchTotal: number;
  mine: Property[];
}

const initialState: PropertiesState = {
  searchResults: [],
  searchTotal: 0,
  mine: [],
};

/** Caches explorer results and owner dashboard rows. */
const propertiesSlice = createSlice({
  name: "properties",
  initialState,
  reducers: {
    setSearch(state, action: PayloadAction<{ items: Property[]; total: number }>) {
      state.searchResults = action.payload.items;
      state.searchTotal = action.payload.total;
    },
    setMine(state, action: PayloadAction<Property[]>) {
      state.mine = action.payload;
    },
  },
});

export const { setSearch, setMine } = propertiesSlice.actions;
export default propertiesSlice.reducer;
