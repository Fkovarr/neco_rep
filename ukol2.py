import csv
import geocoder
from typing import List, Iterable, Any, Iterator
from math import sqrt, sin, cos, atan2, radians

EARTH_RADIUS = 6371


class Coordinate:
    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = latitude
        self.longitude = longitude

    def __iter__(self) -> Iterator[float]:
        return iter((self.latitude, self.longitude))

    @staticmethod
    def distance(c1: 'Coordinate', c2: 'Coordinate') -> float:
        dlat = radians(c2.latitude - c1.latitude)
        dlon = radians(c2.longitude - c1.longitude)
        a = sin(dlat / 2) * sin(dlat / 2) + radians(c1.latitude) * cos(
            radians(c2.latitude)
        ) * sin(dlon / 2) * sin(dlon / 2)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return EARTH_RADIUS * c  # distance in km


class City(Coordinate):
    def __init__(self, name: str, latitude: float, longitude: float) -> None:
        super().__init__(latitude, longitude)
        self.name = name


def parse_coordinates(path: str) -> List[Coordinate]:
    coordinates: List[Coordinate] = []
    with open(path, 'r', encoding='utf-8') as file:
        reader = iter(csv.DictReader(file))
        while (latitude := next(reader, None)) is not None:
            longitude = next(reader, None)
            if longitude is None:
                raise ValueError('Invalid coordinates file')
            coordinates.append(
                Coordinate(float(latitude['value']), float(longitude['value']))
            )
    return coordinates


def parse_cities(path: str) -> List[City]:
    cities: List[City] = []
    with open(path, 'r', encoding='utf-8') as file:
        next(file)  # skip header
        for i, line in enumerate(file):
            line = line.strip()  # remove newline
            try:
                geo = geocode(line, method='reverse')
                cities.append(City(line, geo['lat'], geo['lng']))
            except Exception:
                print('Failed to find location of:', line)
    return cities


def write_coordinates(path: str, coordinates: Iterable[Coordinate]) -> None:
    with open(path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(
            ['latitude', 'longitude', 'country', 'city', 'address']
        )
        for latitude, longitude in coordinates:
            try:
                geo = geocode([latitude, longitude], method='reverse')
                writer.writerow(
                    [
                        latitude,
                        longitude,
                        geo['country'],
                        geo['city'],
                        geo['address'],
                    ]
                )
            except Exception:
                print('Failed to find city:', f'[{latitude}, {longitude}]')


def write_closest_cities(
    path: str,
    coordinates: Iterable[Coordinate],
    cities: Iterable[City],
) -> None:
    with open(path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['longitude', 'longtitude', 'city'])
        for coordinate in coordinates:
            closest_city = min(
                cities, key=lambda city: Coordinate.distance(city, coordinate)
            )
            writer.writerow(
                [
                    coordinate.latitude,
                    coordinate.longitude,
                    closest_city.name,
                ]
            )


def geocode(location: Any, **kwargs: Any) -> Any:
    geo = geocoder.arcgis(location, **kwargs)
    return geo.json


def main() -> None:
    coordinates = parse_coordinates('coordinates.csv')
    cities = parse_cities('world-cities - kopie.csv')
    write_coordinates('coordinates_with_info5.csv', coordinates)
    write_closest_cities('closest_cities5.csv', coordinates, cities)


if __name__ == "__main__":
    main()