# Welcome to Coruscant Health Administration

## Task

Build a hospital administration system for the Coruscant Health Administration (CHA) using Django.

The system manages patients, doctors, departments, service orders (appointments/scans), medical records, and administration.

## Description

This project is a Django web application for managing hospital information for Coruscant Health.

It allows users to:

* Register and manage patients
* Register and manage doctors
* Register and manage departments (imaging, labs, etc.)
* Create and manage service orders (CT scan, PET scan, MRI, X-ray, blood test, ultrasound)
* Create and manage medical records (device readings, prescriptions, encrypted documents)
* Approve or reject new Patient/Doctor/Department registrations (Administrator)
* Fast-track new patient intake (Emergency Services)

## Installation

Clone the project:

git clone https://github.com/FaganAliyevvvv/Coruscant-Health-Administration.git

cd Coruscant-Health-Administration

Install dependencies:

pip install -r requirements.txt

Set required environment variables:

linux:

export DJANGO_SECRET_KEY="dev-secret-key"
export DOCUMENT_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

windows:

$env:DJANGO_SECRET_KEY = "dev-secret-key"; $env:DOCUMENT_ENCRYPTION_KEY = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

Run migrations:

python manage.py migrate

Create the first Administrator account:

python manage.py bootstrap_admin --username admin --password "change-me-now"

Start the server:
python manage.py runserver

Open:

http://127.0.0.1:8000/

## Usage

Open the home page and register as a Patient, Doctor, or Department, or log in as the Administrator.

* **Patients** upload device readings, view their vitals history, and read doctor prescriptions.
* **Doctors** view patient records, write prescriptions/reports, and order services (CT scan, PET scan, etc.).
* **Departments** receive orders in a queue, accept them, and upload results.
* **Emergency Services** register new patients instantly without waiting for approval.
* **Administrators** approve new Patient/Doctor/Department accounts and manage all data from `/admin/`.

New Patient, Doctor, and Department accounts require Administrator approval before they can use their dashboard features.

### The Core Team

Fagan Aliyev

<span><i>Made at <a href='https://qwasar.io'>Qwasar SV -- Software Engineering School</a></i></span>

<span><img alt='Qwasar SV -- Software Engineering School Logo' src='https://storage.googleapis.com/qwasar-public/qwasar-logo_50x50.png' width='20px' /></span>
