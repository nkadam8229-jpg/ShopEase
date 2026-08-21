# ShopEase

ShopEase is a deployment-focused e-commerce application developed as the
workload for a cloud and infrastructure deployment project.

The application provides realistic customer and administrator workflows,
including product browsing, authentication, wishlist, cart, checkout,
order placement, order lifecycle management, and administration.

## Purpose

The application was built to provide a realistic workload for experimenting
with and documenting different deployment and infrastructure approaches.

Instead of creating a simple demonstration application, the project includes
common e-commerce workflows such as product browsing, authentication, wishlist,
cart, checkout, order placement, administration, image management, and order
lifecycle processing.

This makes the application suitable for later deployment and testing with
different infrastructure approaches such as:

- AWS cloud infrastructure
- Load balancing
- Auto Scaling
- Managed databases
- Object storage
- Docker
- Kubernetes
- Traffic and performance testing

The application itself is therefore the workload, while the infrastructure
and deployment technologies are separate parts of the overall project.

## Technology Stack

### Application

- Python
- Flask
- Jinja2 / HTML
- CSS
- JavaScript

### Database

- MySQL
- SQLAlchemy / Flask-SQLAlchemy
- PyMySQL

### Storage

- Local filesystem storage
- Local `uploads/` directories for application images

### Other

- Git / GitHub
- k6 for traffic and load testing

## Application Documentation

For a detailed explanation of the ShopEase application:

[Application Documentation](docs/application/PROJECT_DOCUMENTATION.md)

## Deployment Documentation

### Local Storage / EC2

The local-storage version can be deployed on an Ubuntu EC2 instance using
the following guide:

[Local Storage EC2 Deployment](docs/application/LOCAL_STORAGE_EC2_DEPLOYMENT.md)

### AWS RDS + S3

The RDS + S3 implementation is maintained separately in the `main` branch.

### Docker

Docker deployment documentation will be added later.

### Kubernetes

Kubernetes deployment documentation will be added later.

## Repository Structure

```text
app/        → Application source code
database/   → Database structure
static/     → CSS, JavaScript and static assets
templates/  → Application HTML templates
docs/       → Project and deployment documentation
