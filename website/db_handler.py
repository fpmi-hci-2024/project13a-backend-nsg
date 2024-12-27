from flask import Blueprint, request, jsonify
from website.models import Station, Route, RouteStop
from datetime import datetime, timedelta
from . import db

db_handler = Blueprint('db_handler', __name__)

@db_handler.route('/fill', methods=['GET'])
def handler():
    # Очистим таблицы
    db.session.query(Station).delete()
    db.session.query(Route).delete()
    db.session.query(RouteStop).delete()

    # Создание станций
    stations = [
        "Минск",
        "Гомель",
        "Могилев",
        "Брест",
        "Витебск",
        "Гродно",
        "Бобруйск",
        "Пинск",
        "Орша",
        "Барсуки"
    ]

    # Добавляем станции в БД
    for station_name in stations:
        station = Station(name=station_name, latitude=0.0, longitude=0.0)  # Широта и долгота можно оставить заглушками
        db.session.add(station)

    db.session.commit()

    # Пример маршрутов и остановок
    routes_data = [
        {
            'route_name': "Маршрут 1",
            'stations': ["Минск", "Гомель", "Могилев"],
            'departure_times': ["2025-12-21T08:00:00", "2025-12-21T10:00:00", "2025-12-21T12:00:00"]
        },
        {
            'route_name': "Маршрут 2",
            'stations': ["Брест", "Гродно", "Минск"],
            'departure_times': ["2025-12-21T09:00:00", "2025-12-21T11:00:00", "2025-12-21T13:00:00"]
        },
        {
            'route_name': "Маршрут 3",
            'stations': ["Могилев", "Минск", "Гомель"],
            'departure_times': ["2024-12-21T07:30:00", "2024-12-21T09:30:00", "2025-12-21T11:30:00"]
        },
        {
            'route_name': "Маршрут 4",
            'stations': ["Брест", "Гродно", "Минск", "Гомель", "Могилев", "Витебск"],
            'departure_times': ["2025-12-21T07:30:00", "2025-12-21T09:30:00", "2025-12-21T11:30:00", "2025-12-22T07:30:00", "2025-12-22T09:30:00", "2025-12-22T11:30:00"]
        }
    ]

    # Добавляем маршруты и остановки в БД
    for route_data in routes_data:
        route = Route(name=route_data['route_name'])
        db.session.add(route)
        db.session.commit()  # Сохраняем маршрут, чтобы получить его id

        # Добавляем остановки
        for idx, station_name in enumerate(route_data['stations']):
            station = Station.query.filter_by(name=station_name).first()
            stop_time = datetime.fromisoformat(route_data['departure_times'][idx])

            route_stop = RouteStop(
                route_id=route.id,
                station_id=station.id,
                time_of_arrival=stop_time - timedelta(minutes=15),  # Допустим, что поезд прибывает за 15 минут до отправления
                time_of_departure=stop_time,
                stop_order=idx + 1
            )
            db.session.add(route_stop)

    db.session.commit()

    return jsonify({'done': 'done'})