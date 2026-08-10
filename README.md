# E-Challan-Management-System
🚦 E-Challan Management System — A web-based DBMS project for managing traffic violations, registered vehicles, challans, police records, and payments using Python Flask and MySQL.

**🚦 E-Challan Management System**

#The E-Challan Management System is a web-based application developed as a DBMS mini project to digitally manage traffic violations and challan payments.

The system allows vehicle owners to search their challan details using their vehicle registration number, while authorized police officers can log in and manage registered vehicles, issue challans, record violation locations and times, and process payments.

**🛠️ Technologies Used**
Frontend: HTML, CSS

Backend: Python

Framework: Flask

Database: MySQL

Database Connector: MySQL Connector/Python


*For your E-Challan Management System, you can define three main roles:*


**👮 Police Role**

*The Police module is responsible for managing traffic violations and challans.*

1. Police officer login/logout
2. Search registered vehicles
3. Verify vehicle registration
4. Add new traffic challans
5. Select violation type
6. Enter violation location
7. Automatically record violation date and time
8. Set fine amount
9. View all challan records
10. Search challans by vehicle number
11. Process cash payments
12. Update challan status from Unpaid → Paid
13. View payment mode and transaction details


**🛡️ Admin Role**

*The Admin module manages the overall system and database.*

1. Admin login/logout
2. Manage police officer accounts
3. Add, update, and remove police details
4. Manage registered vehicles
5. View all challans
6. View all payment records
7. Monitor paid and unpaid challans
8. Manage database records
9. Generate reports
10. Maintain system security and access control


**👤 Public/User Role**

*The Public module allows vehicle owners to check their challan information.*

1. Enter vehicle registration number
2. View unpaid challans
3. View challan ID
4. View vehicle number
5. View violation
6. View violation location
7. View violation date and time
8. View fine amount
9. View payment status
10. Pay using UPI or Card
11. View payment confirmation
12. Role Summary


*Role	Main Responsibilities*
| Role           | Main Responsibilities                                         |
| -------------  | ------------------------------------------------------------- |
| 👮 **Police** | Issue challans, manage violations, collect cash payments       |
| 🛡️ **Admin**  | Manage users, police, vehicles, challans, payments and system  |
| 👤 **Public** | Search challans and make online payments                       |


Access flow:

                    E-CHALLAN SYSTEM
                          │
          ┌───────────────┼───────────────┐
          │               │               │
       ADMIN            POLICE          PUBLIC
          │               │               │
     System Mgmt      Challan Mgmt    Search Challan
     Police Mgmt      Vehicle Check   View Fine
     Vehicle Mgmt     Cash Payment    UPI/Card Payment
     Reports          Records         Payment Status


**Database Tables – E-Challan Management System**
1. RegisteredVehicle
2. Challan
3. Payment
4. Police_Details
5. Police


**1. RegisteredVehicle**
*The RegisteredVehicle table stores information about vehicles that are officially registered in the system. A challan can be issued only for a registered vehicle.*
| Column          | Description                 |
| --------------- | --------------------------- |
| `reg_no` **PK** | Vehicle registration number |
| `owner_name`    | Name of vehicle owner       |
| `vehicle_type`  | Type of vehicle             |
| `model`         | Vehicle model               |
| `color`         | Vehicle color               |
| `mobile_no`     | Owner's mobile number       |
| `address`       | Owner's address             |
Primary Key: police_id


**2. Police_Details**
*The Police_Details table stores personal and professional information about police officers.*
| Column             | Description              |
| ------------------ | ------------------------ |
| `police_id` **PK** | Unique police officer ID |
| `officer_name`     | Name of police officer   |
| `badge_number`     | Police badge number      |
| `rank_name`        | Officer's rank           |
| `mobile_no`        | Officer's mobile number  |
| `address`          | Officer's address        |
Primary Key: login_id
Foreign Key: police_id → Police_Details(police_id)


**4. Challan**
*The Challan table is the main table for storing traffic violation records.*
| Column           | Description                       |
| ---------------- | --------------------------------- |
| `id` **PK**      | Unique challan ID                 |
| `reg_no` **FK**  | Vehicle registration number       |
| `violation`      | Type of traffic violation         |
| `location`       | Location where violation occurred |
| `violation_time` | Date and time of violation        |
| `fine`           | Fine amount                       |
| `status`         | Paid / Unpaid                     |
| `payment_mode`   | UPI / Card / Cash                 |

Primary Key: id
Foreign Key: reg_no → RegisteredVehicle(reg_no)


id       : 202605
reg_no   : KA01A0001
violation: No Helmet
location : MG Road
fine     : ₹500
status   : Unpaid

**5. Payment**
*The Payment table stores payment transactions made against challans.*
| Column              | Description                  |
| ------------------- | ---------------------------- |
| `payment_id` **PK** | Unique payment ID            |
| `challan_id` **FK** | References the challan       |
| `reg_no` **FK**     | Vehicle registration number  |
| `amount`            | Amount paid                  |
| `payment_mode`      | UPI / Card / Cash            |
| `payment_date`      | Date of payment              |
| `transaction_id`    | Unique transaction reference |
| `payment_status`    | Payment status               |

Primary Key: payment_id
Foreign Keys: challan_id → Challan(id)
reg_no → RegisteredVehicle(reg_no)



**Command to create a DataBase**
Create a Database
```CREATE DATABASE IF NOT EXISTS echallan;```
```USE echallan;```


**1. RegisteredVehicle**

```sql
CREATE TABLE RegisteredVehicle (
    reg_no VARCHAR(20) PRIMARY KEY,
    owner_name VARCHAR(100),
    vehicle_type VARCHAR(50),
    model VARCHAR(50),
    color VARCHAR(30),
    mobile_no VARCHAR(15),
    address VARCHAR(200)
);
```

**2. Police_Details**
```sql
CREATE TABLE Police_Details (
    police_id INT PRIMARY KEY AUTO_INCREMENT,
    officer_name VARCHAR(100),
    badge_number VARCHAR(50),
    rank_name VARCHAR(50),
    mobile_no VARCHAR(15),
    address VARCHAR(200)
);
```

**3. Challan**
```sql
CREATE TABLE Challan (
    id INT PRIMARY KEY AUTO_INCREMENT,
    reg_no VARCHAR(20),
    violation VARCHAR(100),
    location VARCHAR(100),
    violation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fine INT,
    status VARCHAR(20) DEFAULT 'Unpaid',
    payment_mode VARCHAR(20),
    CONSTRAINT fk_challan_vehicle
    FOREIGN KEY (reg_no)
    REFERENCES RegisteredVehicle(reg_no)
);
```

**4. Payment**
```sql
CREATE TABLE Payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    challan_id INT,
    reg_no VARCHAR(20),
    amount INT,
    payment_mode VARCHAR(20),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_id VARCHAR(100),
    payment_status VARCHAR(20) DEFAULT 'Success',

    CONSTRAINT fk_payment_challan
    FOREIGN KEY (challan_id)
    REFERENCES Challan(id),

    CONSTRAINT fk_payment_vehicle
    FOREIGN KEY (reg_no)
    REFERENCES RegisteredVehicle(reg_no)
);
```

**5. 5. Police**
```sql
CREATE TABLE Police (
    login_id INT PRIMARY KEY AUTO_INCREMENT,
    police_id INT,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(100),

    CONSTRAINT fk_police_details
    FOREIGN KEY (police_id)
    REFERENCES Police_Details(police_id)
);
```


SHOW TABLES;

**Check table structures**

```sql
DESC RegisteredVehicle;

DESC Police_Details;

DESC Police;

DESC Challan;

DESC Payment;
```

***Then run your Flask project***

Open Command Prompt / VS Code Terminal in your project folder:

``cd C:\Users\bhanu\OneDrive\Desktop\e_challan``

Install dependencies if needed:

``pip install flask mysql-connector-python``

Then run:

``python app.py``

You should see something similar to:

``* Running on http://127.0.0.1:5000``

Open your browser and go to:

``http://127.0.0.1:5000``

Your E-Challan Management System should now open.


**🎯 Project Objective**

The main objective is to reduce manual paperwork and provide an efficient, centralized system for managing traffic violations, challans, registered vehicles, and payments while demonstrating practical DBMS concepts such as normalization, primary keys, foreign keys, triggers, views, and relational database design.

****

Suggested GitHub topics:
python flask mysql dbms e-challan traffic-management html css database-project crud
