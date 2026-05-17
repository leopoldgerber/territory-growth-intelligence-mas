import type { CountryItem } from '../api/client';

type CountrySelectorProps = {
  countries: CountryItem[];
  countryId: number | null;
  onCountryChange: (countryId: number) => void;
};

export function CountrySelector({ countries, countryId, onCountryChange }: CountrySelectorProps) {
  return (
    <label>
      <span>Country</span>
      <select
        value={countryId ?? ''}
        onChange={(event) => onCountryChange(Number(event.target.value))}
      >
        <option value="">Select country</option>
        {countries.map((country) => (
          <option key={country.country_id} value={country.country_id}>
            {country.country_name_en}
          </option>
        ))}
      </select>
    </label>
  );
}
