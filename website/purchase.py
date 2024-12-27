from flask import Blueprint, request, jsonify
from .models import Ticket, User, Route, RouteStop, Station
from . import db
from datetime import datetime
from .auth_utils import verify_token

purchase = Blueprint('purchase', __name__)

@purchase.route('/tickets', methods=['GET'])
def get_tickets():
    user_id = verify_token()

    if isinstance(user_id, tuple):
        return user_id

    # Получаем пользователя
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Получаем все билеты пользователя
    tickets = Ticket.query.filter_by(user_id=user.id).all()

    if tickets:
        tickets_data = []
        for ticket in tickets:
            stop_of_departure = RouteStop.query.get(ticket.stop_of_departure_id)
            stop_of_arrival = RouteStop.query.get(ticket.stop_of_arrival_id)

            tickets_data.append({
                'ticketID': ticket.id,
                'routeID': ticket.route_id,
                'stopOfDeparture': {
                    'timeOfArrival': stop_of_departure.time_of_arrival,
                    'timeOfDeparture': stop_of_departure.time_of_departure,
                    'orderIndex': stop_of_departure.stop_order,
                    'station': {
                        'id': stop_of_departure.station_id,
                        'name': Station.query.get(stop_of_departure.station_id).name
                    }
                },
                'stopOfArrival': {
                    'timeOfArrival': stop_of_arrival.time_of_arrival,
                    'timeOfDeparture': stop_of_arrival.time_of_departure,
                    'orderIndex': stop_of_arrival.stop_order,
                    'station': {
                        'id': stop_of_arrival.station_id,
                        'name': Station.query.get(stop_of_arrival.station_id).name
                    }
                },
                'price': ticket.price
            })
        return jsonify({'tickets': tickets_data}), 200

    return jsonify({'message': 'No tickets found for this user'}), 404

@purchase.route('/tickets/request', methods=['POST'])
def request_ticket():
    user_id = verify_token()

    if isinstance(user_id, tuple):
        return user_id

    # Получаем данные из запроса
    data = request.json
    route_id = data.get('routeID')
    departure_station_name = data.get('departureRouteStop')
    arrival_station_name = data.get('arrivalRouteStop')
    price = data.get('price')

    if not route_id or not departure_station_name or not arrival_station_name or price is None:
        return jsonify({'error': 'routeID, departureRouteStop, arrivalRouteStop, and price are required'}), 400

    # Проверяем существование маршрута и остановок
    route = Route.query.get(route_id)
    departure_stop = RouteStop.query.join(Station).filter(RouteStop.route_id == route_id, Station.name == departure_station_name).first()
    arrival_stop = RouteStop.query.join(Station).filter(RouteStop.route_id == route_id, Station.name == arrival_station_name).first()

    if not route or not departure_stop or not arrival_stop:
        return jsonify({'error': 'Route or one of the stops does not exist'}), 404

    if departure_stop.stop_order >= arrival_stop.stop_order:
        return jsonify({'error': 'The departure stop must come before the arrival stop'}), 400

    # Создаем новый билет
    ticket = Ticket(
        user_id=user_id,
        route_id=route.id,
        stop_of_departure_id=departure_stop.id,
        stop_of_arrival_id=arrival_stop.id,
        price=price
    )
    db.session.add(ticket)
    db.session.commit()

    return jsonify({'message': 'Ticket purchased successfully'}), 200
