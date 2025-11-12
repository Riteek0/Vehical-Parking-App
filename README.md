# Vehical-Parking
this is dummy project that allows users to book parking spot
# 🚗 Vehicle Parking Management System

## 📖 Project Overview
The Vehicle Parking Management System is a web application designed to streamline the management of parking lots, spots, and reservations. The platform allows **admins** to manage parking lots and monitor usage, while **users** can book parking spots, view their parking history, and manage their reservations.

---

## 📌 Key Features

- 🛡️ **Admin Dashboard:** Manage parking lots, spots, and view user activity.
- 🚙 **User Dashboard:** Book parking spots and view/manage reservation history.
- 🔍 **Advanced Search:** Find lots, spots, and reservations with flexible filters.
- 🔑 **Authentication & Role Management:** Secure login for admins and users.
- 💻 **Responsive UI:** Built with Bootstrap for seamless experience on all devices.


## 🛠️ Technologies Used

- **Flask**: Backend web framework
- **SQLAlchemy & Flask-SQLAlchemy**: ORM for database management  
- **SQLite**: Database engine
- **Bootstrap**: Responsive frontend design (via CDN)
- **Flask-Dotenv & python-dotenv**: Environment variable management

---

## 🚩 Milestones

1. **Database Models and Schema Setup**
   - Defined models for User, ParkingLot, ParkingSpot, and Reservation.
   - Set up relationships and initialized the SQLite database.

2. **Authentication and Role Management**
   - Implemented user registration and login.
   - Role-based access for admin and user dashboards.

3. **Admin Dashboard and Management**
   - Admins can add, edit, and delete parking lots and spots.
   - View all users and their reservation activity.

4. **User Dashboard and Parking Spot Booking**
   - Users can search for available parking lots and book spots.
   - Users can view their reservation history and manage bookings.

5. **Search Functionality**
   - Search for users, lots, spots, and reservations by various fields.
   - Role-based search: admins have full access, users see only their data.

6. **Environment Configuration**
   - Used `.env` file for configuration and secret management.

---

## 🗂️ Models

- **User:** Stores user information, authentication, and role.
- **ParkingLot:** Represents a parking lot with location and pricing.
- **ParkingSpot:** Individual spots within a lot, with status (occupied/available).
- **Reservation:** Tracks bookings, timestamps, and vehicle details.