# ShopEase — Local Storage Deployment Steps

This guide explains how to deploy the **local-storage version** of ShopEase on a fresh Ubuntu EC2 instance.

This version uses:

- Flask for the application
- MySQL running on the same EC2 instance
- Local filesystem storage for uploaded images
- `uploads/` directories on the EC2 instance

This guide is for the `local-storage` branch. It is separate from the current `main` branch, which uses the RDS + S3 implementation.

---

## 1. Create EC2 and Connect

Create an Ubuntu EC2 instance and connect to it from your Windows/local machine.

```bash
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP
```

For the initial direct testing setup, the EC2 Security Group should allow:

- SSH — TCP 22
- Custom TCP — TCP 5000

Port 5000 is used for direct Flask testing. In a later production-style deployment, the application should normally be placed behind a load balancer instead of exposing Flask directly.

---

## 2. Update Ubuntu

```bash
sudo apt update
sudo apt upgrade -y
```

---

## 3. Install Required Packages

Install Python, Git, MySQL, and the Python virtual-environment package:

```bash
sudo apt install -y python3 python3-pip python3-venv git mysql-server
```

Verify the installations:

```bash
python3 --version
git --version
mysql --version
```

---

## 4. Start and Check MySQL

Enable MySQL to start automatically and start it now:

```bash
sudo systemctl enable mysql
sudo systemctl start mysql
```

Check the service:

```bash
sudo systemctl status mysql --no-pager
```

MySQL is used locally on the same EC2 instance for this version.

---

## 5. Clone the ShopEase Repository

Clone only the `local-storage` branch:

```bash
git clone --branch local-storage --single-branch https://github.com/nkadam8229-jpg/ShopEase.git
cd ShopEase
```

The `--branch local-storage` option directly downloads the required branch, while `--single-branch` avoids downloading the other branches.

No separate `git checkout local-storage` step is required.

---

## 6. Create the Python Virtual Environment

Create the virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install the application dependencies:

```bash
pip install -r requirements.txt
```

---

## 7. Create the MySQL Database

Enter MySQL:

```bash
sudo mysql
```

Create the ShopEase database:

```sql
CREATE DATABASE shopease;
```

Create a dedicated MySQL user.

Use your own strong password instead of the example password below:

```sql
CREATE USER 'shopease_user'@'localhost' IDENTIFIED BY 'YOUR_DB_PASSWORD';
```

Grant access:

```sql
GRANT ALL PRIVILEGES ON shopease.* TO 'shopease_user'@'localhost';
```

Apply the privileges:

```sql
FLUSH PRIVILEGES;
```

Exit:

```sql
EXIT;
```

---

## 8. Import the Current Database Structure

The repository contains:

```text
database/shopease_structure.sql
```

Import the database structure:

```bash
mysql -u shopease_user -p shopease < database/shopease_structure.sql
```

Enter the MySQL password created in the previous step.

The database is now structurally ready.

This deployment starts with a fresh database and does not copy the old database records.

---

## 9. Verify the Database Structure

Connect using the ShopEase MySQL user:

```bash
mysql -u shopease_user -p
```

Then run:

```sql
USE shopease;
SHOW TABLES;
```

Verify that the ShopEase tables are present.

Exit:

```sql
EXIT;
```

---

## 10. Create the `.env` File

Create the environment file:

```bash
nano .env
```

Use the local-storage configuration:

```text
FLASK_ENV=development
SECRET_KEY=YOUR_STRONG_SECRET_KEY
DB_HOST=localhost
DB_PORT=3306
DB_NAME=shopease
DB_USER=shopease_user
DB_PASSWORD=YOUR_DB_PASSWORD
STORAGE_TYPE=local
```

Save the file.

Do not commit the real `.env` file or real passwords to GitHub.

The important setting for this branch is:

```text
STORAGE_TYPE=local
```

This tells ShopEase to use the local filesystem storage implementation.

---

## 11. Create Empty Upload Directories

The local-storage version stores uploaded images on the EC2 filesystem.

Create the required directories:

```bash
mkdir -p uploads/products
mkdir -p uploads/categories
mkdir -p uploads/subcategories
mkdir -p uploads/brands
mkdir -p uploads/banners
mkdir -p uploads/profiles
```

Verify:

```bash
ls uploads/
```

Expected directories:

```text
banners
brands
categories
products
profiles
subcategories
```

These directories are initially empty on a fresh deployment.

Old uploaded files are not transferred automatically.

---

## 12. Test the MySQL User

Test the database credentials:

```bash
mysql -u shopease_user -p
```

Enter the database password.

If MySQL opens successfully, the application database credentials are working.

Exit:

```sql
EXIT;
```

---

## 13. Create the First ShopEase Admin

Make sure the virtual environment is active:

```bash
source venv/bin/activate
```

Run:

```bash
python create_admin.py
```

Enter the required administrator details when prompted.

Use a real admin password for the deployment.

The **ShopEase admin password is separate from the MySQL password**.

For example:

```text
MySQL password: YOUR_DB_PASSWORD
ShopEase admin password: YOUR_ADMIN_PASSWORD
```

Do not use example passwords in an actual deployment.

---

## 14. Start ShopEase

Activate the virtual environment if necessary:

```bash
source venv/bin/activate
```

Start the application:

```bash
python run.py
```

The current application listens on:

```text
0.0.0.0:5000
```

Keep this terminal running while testing the application.

---

## 15. Open ShopEase

From a browser on your local machine, open:

```text
http://EC2_PUBLIC_IP:5000
```

Replace `EC2_PUBLIC_IP` with the public IPv4 address of the EC2 instance.

---

## 16. Initial Admin Testing

Because this is a completely fresh installation, configure the catalog from the admin side first.

Recommended sequence:

1. Admin Login
2. Create Categories
3. Create Subcategories
4. Create Brands
5. Create Products
6. Upload Product Images
7. Create Variants
8. Add Banners

Because this is the local-storage version, uploaded images will be stored under the EC2 instance's `uploads/` directory.

---

## 17. Initial Customer Testing

After creating the required catalog data:

1. Register a customer
2. Login
3. Browse Products
4. View Product
5. Add Product to Wishlist
6. Add Product to Cart
7. Manage Cart
8. Proceed to Checkout
9. Place Order
10. Open Order Confirmation
11. Verify the Order Lifecycle

This confirms that the main customer workflow is working on the fresh EC2 installation.

---

## 18. Verify Local Image Storage

After uploading images through the admin interface, check the local directories:

```bash
find uploads -type f
```

Uploaded files should appear under the appropriate `uploads/` directory.

This confirms that:

```text
ShopEase
    ↓
Upload Service
    ↓
Storage Service
    ↓
Local Storage
    ↓
uploads/
```

is working correctly.

---

## 19. Verify the Order Lifecycle

Place a test order from the customer side.

The application uses its controlled order lifecycle rather than a real delivery provider.

The order progresses through the application's defined statuses:

```text
PENDING
   ↓
CONFIRMED
   ↓
SHIPPED
   ↓
DELIVERED
```

The order lifecycle is handled by the application's order lifecycle service.

No external courier or delivery API is required for this deployment.

---

## 20. Important Fresh-Server Behavior

This deployment intentionally starts fresh.

The following are **not copied automatically**:

- Old MySQL records
- Old uploaded images
- Old product catalog data
- Old customer accounts
- Old orders

The Git repository provides the application source code.

The file:

```text
database/shopease_structure.sql
```

provides the database structure.

The `uploads/` directories provide empty locations for newly uploaded images.

Therefore, after deployment, the administrator must recreate the required catalog data and upload the required images.

---

## 21. Complete Command Reference

### Connect

```bash
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP
```

### Update

```bash
sudo apt update
sudo apt upgrade -y
```

### Install

```bash
sudo apt install -y python3 python3-pip python3-venv git mysql-server
```

### MySQL

```bash
sudo systemctl enable mysql
sudo systemctl start mysql
```

### Clone

```bash
git clone --branch local-storage --single-branch https://github.com/nkadam8229-jpg/ShopEase.git
cd ShopEase
```

### Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Create database and user

```bash
sudo mysql
```

Inside MySQL:

```sql
CREATE DATABASE shopease;
CREATE USER 'shopease_user'@'localhost' IDENTIFIED BY 'YOUR_DB_PASSWORD';
GRANT ALL PRIVILEGES ON shopease.* TO 'shopease_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Import structure

```bash
mysql -u shopease_user -p shopease < database/shopease_structure.sql
```

### Create upload directories

```bash
mkdir -p uploads/products
mkdir -p uploads/categories
mkdir -p uploads/subcategories
mkdir -p uploads/brands
mkdir -p uploads/banners
mkdir -p uploads/profiles
```

### Create environment file

```bash
nano .env
```

Set:

```text
STORAGE_TYPE=local
```

along with the database and Flask configuration described earlier.

### Create admin

```bash
source venv/bin/activate
python create_admin.py
```

### Run application

```bash
python run.py
```

Then open:

```text
http://EC2_PUBLIC_IP:5000
```

---

## 22. Final Fresh-Server Setup

The local-storage deployment consists of:

- Ubuntu EC2
- ShopEase Flask application
- Python virtual environment
- Local MySQL database
- Local `uploads/` storage
- Fresh database structure
- Newly created administrator
- Newly created catalog data

The application and database are located on the same EC2 instance in this setup.

This setup is useful for understanding and testing the application before moving to a separated production-style architecture.

---

# 23. Inventory Upload Automation

Once Flask is started, products can be added manually through the application by creating categories, subcategories, brands, filling the product form, and uploading images.

To avoid doing this manually for the complete demo inventory, an inventory automation package is provided.

The automation sets up:

* 4 categories
* 20 subcategories
* Required brands
* 69 products
* Product images

**Approximate time:**

* Base setup: ~2 minutes
* Product import: ~15 minutes

**[Download ShopEase Inventory Automation]**
[Download ShopEase Inventory Automation](https://drive.google.com/file/d/1H6kyRdkIvpi54HEN_fhcDxTzqc296PCD/view?usp=sharing)

> **Important:** The ShopEase application must already be running before starting the inventory automation.

---

## Windows — Recommended

### 1. Download and Extract

Download the inventory ZIP and extract it.

The extracted folder should contain:

* `requirements.txt`
* `base_setup.py`
* `import_products.py`
* `ShopEase_Inventry_25pct/`

The `ShopEase_Inventry_25pct` folder contains:

* `Brands`
* `Categories`
* `Electronics`
* `Home-Decor`
* `Mens-Clothing`
* `Womens-Clothing`

### 2. Open Command Prompt

Open the extracted **`ShopEase_Inventory`** folder in File Explorer.

Stay outside the `ShopEase_Inventry_25pct` folder.

Click the address bar, type:

```text
cmd
```

Press **Enter**.

The Command Prompt will open directly inside the `ShopEase_Inventory` folder.

### 3. Install Required Packages

Verify Python and pip:

```text
python --version
python -m pip --version
```

Install the required packages:

```text
python -m pip install -r requirements.txt
```

### 4. Run Base Setup

Replace `<INVENTORY_FOLDER_PATH>` with the path of your extracted `ShopEase_Inventry_25pct` folder.

```text
python base_setup.py --inventory "<INVENTORY_FOLDER_PATH>" --base-url "http://<PUBLIC_IP>:5000"
```

**Approximate time:** ~2 minutes

### 5. Import Products

After the base setup finishes successfully, run:

```text
python import_products.py --inventory "<INVENTORY_FOLDER_PATH>" --base-url "http://<PUBLIC_IP>:5000"
```

**Approximate time:** ~15 minutes

---

## EC2 / Linux

### 1. Download and Extract

Download the inventory ZIP directly to the EC2 instance:

```bash
wget "https://drive.usercontent.google.com/download?id=1H6kyRdkIvpi54HEN_fhcDxTzqc296PCD&export=download&confirm=t" -O ShopEase_Inventory.zip
```

Extract it:

```bash
unzip ShopEase_Inventory.zip
```

The extracted folder will be:

```text
ShopEase_Inventory/
```

It contains:

* `requirements.txt`
* `base_setup.py`
* `import_products.py`
* `ShopEase_Inventry_25pct/`

The `ShopEase_Inventry_25pct` folder contains:

* `Brands`
* `Categories`
* `Electronics`
* `Home-Decor`
* `Mens-Clothing`
* `Womens-Clothing`

### 2. Open the Inventory Automation Folder

```bash
cd ShopEase_Inventory
```

### 3. Install Required Packages

Verify Python and pip:

```bash
python3 --version
python3 -m pip --version
```

Install the required packages:

```bash
python3 -m pip install -r requirements.txt
```

### 4. Run Base Setup

Replace `<INVENTORY_FOLDER_PATH>` with the path of the extracted `ShopEase_Inventry_25pct` folder.

```bash
python3 base_setup.py --inventory "<INVENTORY_FOLDER_PATH>" --base-url "http://<PUBLIC_IP>:5000"
```

**Approximate time:** ~2 minutes

### 5. Import Products

After the base setup finishes successfully, run:

```bash
python3 import_products.py --inventory "<INVENTORY_FOLDER_PATH>" --base-url "http://<PUBLIC_IP>:5000"
```

**Approximate time:** ~15 minutes

> Replace `<PUBLIC_IP>` with the IP address where the ShopEase Flask application is running.

---


## 24. Difference from the `main` Branch

The `local-storage` branch and `main` branch contain the same core ShopEase application workflow, but they use different infrastructure/storage implementations.

### `local-storage`

- MySQL runs locally.
- Images are stored locally.
- `STORAGE_TYPE=local`.
- Suitable for local development, testing, and simple EC2 deployment.

### `main`

- Uses the RDS + S3 implementation.
- MySQL is intended to run on Amazon RDS.
- Application images are intended to use Amazon S3.
- Suitable as the current application version for the later AWS architecture.

The AWS deployment documentation will be maintained separately and should not be mixed into this application setup guide.

---

## 25. Important Security Notes

For a real deployment:

- Use a strong database password.
- Use a strong Flask `SECRET_KEY`.
- Do not commit `.env` to GitHub.
- Do not expose MySQL port 3306 publicly.
- Restrict SSH access where possible.
- Port 5000 is being used here for direct testing only.
- For a production-style AWS deployment, the application should later be placed behind an ALB and protected with appropriate security groups.

This guide is intended for the **local-storage deployment path** and does not represent the final production AWS architecture.
