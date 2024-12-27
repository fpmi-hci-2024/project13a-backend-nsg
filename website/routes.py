from flask import Blueprint, request, jsonify
from datetime import datetime
from .models import Route, RouteStop, Station
from . import db
from sqlalchemy.orm import aliased

routes = Blueprint('routes', __name__)

@routes.route('/search', methods=['POST'])
def search():
    # Получаем данные из запроса
    data = request.json
    station_from_name = data.get('departure')
    station_to_name = data.get('arrival')

    print(station_from_name)
    print(station_to_name)

    if not station_from_name or not station_to_name:
        return jsonify({'error': 'Both departure and arrival must be provided'}), 400

    # Получаем текущее время
    current_time = datetime.utcnow()

    # Поиск станций по именам
    station_from = Station.query.filter_by(name=station_from_name).first()
    station_to = Station.query.filter_by(name=station_to_name).first()

    if not station_from or not station_to:
        return jsonify({'error': 'One or both of the stations do not exist'}), 404

    # Создаем алиасы для RouteStop
    route_stop_from = aliased(RouteStop)
    route_stop_to = aliased(RouteStop)

    # Ищем маршруты, которые проходят через обе станции и идут от станции_from к станции_to
    routes = db.session.query(Route).join(route_stop_from, Route.id == route_stop_from.route_id).filter(
        route_stop_from.station_id == station_from.id,
        route_stop_from.time_of_departure >= current_time
    ).join(route_stop_to, Route.id == route_stop_to.route_id).filter(
        route_stop_to.station_id == station_to.id
    ).filter(route_stop_from.stop_order < route_stop_to.stop_order).all()  # Проверка порядка остановок

    if routes:
        routes_data = [
            {
                'route_id': route.id,
                'route_name': route.name
            } for route in routes
        ]
        return jsonify({'routes': routes_data}), 200

    # Если маршруты не найдены
    return jsonify({'message': 'No routes found between the specified stations'}), 404

@routes.route('/route', methods=['GET'])
def route_details():
    # Поиск маршрута по ID

    data = request.json
    route_id = data.get('routeID')

    route = Route.query.get(route_id)

    if not route:
        return jsonify({'error': 'Route not found'}), 404

    # Получаем остановки для маршрута, отсортированные по порядку
    stops = RouteStop.query.filter_by(route_id=route.id).order_by(RouteStop.stop_order).all()
    stops_data = [
        {
            'timeOfArrival': stop.time_of_arrival,
            'timeOfDeparture': stop.time_of_departure,
            'orderIndex': stop.stop_order,
            'station': {
                'id': stop.station_id,
                'name': Station.query.get(stop.station_id).name
            }
        } for stop in stops
    ]

    route_data = {
        'name': route.name,
        'stops': stops_data
    }

    return jsonify(route_data), 200
