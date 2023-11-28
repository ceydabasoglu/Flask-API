from flask import Flask, jsonify, request, make_response
from flasgger import Swagger
from config import get_connection
import jwt
import datetime
from functools import wraps
from flask_cors import CORS

SECRET_KEY = "ceydabasoglu"
app = Flask(__name__)
swagger = Swagger(app, template_file='swagger.yml')
CORS(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Token'ı header'dan al
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token eksik!'}), 401

        try:
            # Token'ı doğrula
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token süresi doldu!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Geçersiz token!'}), 401

        return f(*args, **kwargs)

    return decorated


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return make_response('Giriş bilgileri eksik!', 400)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ceydabasoglu.[User] WHERE Username=?", (data['username'],))
    user = cursor.fetchone()
    
    conn.close()

    if user and user[3] == data['password']:
        token_payload = {
            'username': user[2],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token}), 200
    else:
        return make_response('Kullanıcı adı veya şifre hatalı!', 401)



# Endpoint to fetch data from Azure SQL database with paging
@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()

            # Get page and page_size parameters from the query string
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))

            # Calculate the offset based on the page and page_size
            offset = (page - 1) * page_size

            # Include the schema name in your query and apply paging
            cursor.execute('''
                SELECT * FROM ceydabasoglu.[User]
                ORDER BY idUser
                OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            ''', (offset, page_size))

            users = cursor.fetchall()
            conn.close()

            return jsonify({'users': users}), 200
        else:
            return jsonify({'error': 'Failed to establish connection to database'}), 500

    except Exception as e:
        return jsonify({'error': f'Error retrieving users: {str(e)}'}), 500

    


@app.route('/houses', methods=['GET'])
def get_houses():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        # Include the schema name in your query
        cursor.execute('SELECT * FROM ceydabasoglu.House')  # Use the correct schema.table format
        houses = cursor.fetchall()
        conn.close()
        return jsonify({'houses': houses}), 200
    else:
        return jsonify({'error': 'Failed to establish connection to database'}), 500


@app.route('/houses', methods=['POST'])
@token_required
def create_house():
    data = request.get_json()

    # Veritabanına yeni bir house ekle
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO [ceydabasoglu].House (priceHouse, HouseDescription, HouseAmenities, HouseCity, AvailableStart, AvailableEnd)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['priceHouse'], data['HouseDescription'], data['HouseAmenities'], data['HouseCity'], data['AvailableStart'], data['AvailableEnd']))

        conn.commit()
        conn.close()

        return jsonify({'message': 'House created successfully'}), 201

    except Exception as e:
        return jsonify({'error': f'Error creating house: {str(e)}'}), 500

@app.route('/houses/<int:house_id>', methods=['PUT'])
@token_required
def update_house(house_id):
    data = request.get_json()

    # Veritabanındaki belirli bir house'u güncelle
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE [ceydabasoglu].House
            SET priceHouse = ?, HouseDescription = ?, HouseAmenities = ?, HouseCity = ?, AvailableStart = ?, AvailableEnd = ?
            WHERE idHouse = ?
        ''', (data['priceHouse'], data['HouseDescription'], data['HouseAmenities'], data['HouseCity'], data['AvailableStart'], data['AvailableEnd'], house_id))

        conn.commit()
        conn.close()

        return jsonify({'message': 'House updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': f'Error updating house: {str(e)}'}), 500

@app.route('/houses/<int:house_id>', methods=['DELETE'])
@token_required
def delete_house(house_id):
    # Veritabanındaki belirli bir house'u sil
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM [ceydabasoglu].House WHERE idHouse = ?', (house_id,))

        conn.commit()
        conn.close()

        return jsonify({'message': 'House deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': f'Error deleting house: {str(e)}'}), 500

@app.route('/bookings', methods=['GET'])
def get_bookings():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        # Include the schema name in your query
        cursor.execute('SELECT * FROM [ceydabasoglu].Booking')  
        bookings = cursor.fetchall()
        conn.close()
        return jsonify({'bookings': bookings}), 200
    else:
        return jsonify({'error': 'Failed to establish connection to database'}), 500
    

@app.route('/bookings', methods=['POST'])
@token_required
def create_booking():
    data = request.get_json()

    # Veritabanına yeni bir booking ekle
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO [ceydabasoglu].Booking (BookingDate, StayStart, StayEnd, NumberOfPeople, User_idUser, House_idHouse)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['BookingDate'], data['StayStart'], data['StayEnd'], data['NumberOfPeople'], data['User_idUser'], data['House_idHouse']))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Booking created successfully'}), 201

    except Exception as e:
        return jsonify({'error': f'Error creating booking: {str(e)}'}), 500
    
# Endpoint to delete a booking
@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
@token_required
def delete_booking(booking_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if the booking exists
        cursor.execute('SELECT * FROM [ceydabasoglu].Booking WHERE idBooking = ?', (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        # Delete the booking
        cursor.execute('DELETE FROM [ceydabasoglu].Booking WHERE idBooking = ?', (booking_id,))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        # Return a success response
        return jsonify({'message': 'Booking deleted successfully'}), 200

    except Exception as e:
        # Handle database errors
        return jsonify({'error': f'Error deleting booking: {str(e)}'}), 500

    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
    
