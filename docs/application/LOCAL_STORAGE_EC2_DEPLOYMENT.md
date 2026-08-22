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

## 16. Verify ShopEase Admin Login

Open the ShopEase Admin Login page and sign in using the administrator credentials created earlier.

Confirm that the Admin panel opens successfully.

**This step only verifies that Admin Login is working.**

Catalog creation and product/image population are handled in the optional inventory automation step below.

---

# 17. Inventory Upload Automation — Optional Convenience

The inventory automation is **optional**. It is provided as a convenience so that the complete prepared demo inventory does not have to be entered manually through the Admin interface.

The automation can prepare and import:

- 4 categories
- 20 subcategories
- Required brands
- 69 products
- Product images

**Approximate time:**

- Base setup: ~2 minutes
- Product import: ~15 minutes

> **Important:** ShopEase must already be running and Admin Login must have been verified successfully before starting the automation.

### Windows — Recommended

#### 1. Download and Extract

Download the inventory automation ZIP:

[Download ShopEase Inventory Automation ZIP](https://drive.google.com/file/d/1oB5b7vVpxxDruLHUZWVyaDsxjxM7NW-3/view?usp=sharing)

Extract the downloaded ZIP to any location on the Windows PC.

The extracted `ShopEase_Inventory` folder should contain:

```text
requirements.txt
base_setup.py
import_products.py
ShopEase_Inventry_25pct/
```

The `ShopEase_Inventry_25pct` folder contains:

```text
Brands
Categories
Electronics
Home-Decor
Mens-Clothing
Womens-Clothing
```

#### 2. Open Command Prompt

Open the extracted **`ShopEase_Inventory`** folder in File Explorer.

Stay outside the `ShopEase_Inventry_25pct` folder.

Click the address bar, type:

```text
cmd
```

Press **Enter**.

The Command Prompt will open directly inside the `ShopEase_Inventory` folder.

#### 3. Automatically Install the Required Environment

The automation package can be used on a fresh Windows PC. No manual Python installation or PATH configuration is required.

Run this command:

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $url='https://www.python.org/ftp/python/3.13.15/python-3.13.15-amd64.exe'; $installer=Join-Path $env:TEMP 'python-3.13.15-amd64.exe'; Invoke-WebRequest -Uri $url -OutFile $installer; Start-Process $installer -ArgumentList '/quiet','InstallAllUsers=1','PrependPath=0','Include_test=0','TargetDir=C:\ShopEasePython' -Wait; Remove-Item $installer -Force; & 'C:\ShopEasePython\python.exe' -m venv '.venv'; & '.\.venv\Scripts\python.exe' -m pip install --upgrade pip; & '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt; & '.\.venv\Scripts\python.exe' -m playwright install chromium; Write-Host ''; Write-Host 'ShopEase Inventory environment setup completed successfully.' -ForegroundColor Green"
```

This automatically:

- Downloads Python 3.13.15
- Installs Python silently
- Creates `.venv` inside the current `ShopEase_Inventory` folder
- Upgrades pip
- Installs the packages from `requirements.txt`
- Installs Playwright
- Installs Playwright Chromium

No manual PATH configuration is required.

#### 4. Verify Python

Run:

```cmd
.venv\Scripts\python.exe --version
```

Expected:

```text
Python 3.13.15
```

#### 5. Verify Pillow and Playwright

Run:

```cmd
.venv\Scripts\python.exe -c "from PIL import Image; import playwright; print('Pillow OK'); print('Playwright OK')"
```

Expected:

```text
Pillow OK
Playwright OK
```

#### 6. Run Base Setup

Use the inventory folder relative to the current `ShopEase_Inventory` folder:

```cmd
.venv\Scripts\python.exe base_setup.py --inventory ".\ShopEase_Inventry_25pct" --base-url "http://<PUBLIC_IP>:5000"
```

Replace `<PUBLIC_IP>` with the public IP address of the ShopEase EC2 instance.

No fixed Windows inventory path is required.

After running the command:

1. A Playwright Chromium browser window will open.
2. Log in using your ShopEase Admin credentials.
3. Confirm that the Admin panel opens successfully.
4. Return to the Command Prompt.
5. Press **Enter** to continue.

**Important:** Do not press Enter until Admin Login has been completed successfully.

**Approximate time:** ~2 minutes

#### 7. Import Products

After the base setup finishes successfully, run:

```cmd
.venv\Scripts\python.exe import_products.py --inventory ".\ShopEase_Inventry_25pct" --base-url "http://<PUBLIC_IP>:5000"
```

After running the command:

1. A Playwright Chromium browser window will open.
2. Log in using your ShopEase Admin credentials.
3. Confirm that the Admin panel opens successfully.
4. Return to the Command Prompt.
5. Press **Enter** to continue.

**Important:** Do not press Enter until Admin Login has been completed successfully.

**Approximate time:** ~15 minutes

The automation imports the prepared products and associated images.

---

## 18. Initial Customer Testing

After the required catalog data has been created or imported:

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

## 19. Verify Local Image Storage

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

## 20. Verify the Order Lifecycle

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

## 21. Important Fresh-Server Behavior

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

Therefore, after deployment, the administrator must recreate or import the required catalog data and upload the required images.

---

## 22. Complete Command Reference

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

## 23. Final Fresh-Server Setup

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
