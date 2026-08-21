
---

# `local-storage` branch — put this in `README.md`

Use this version on the `local-storage` branch:

```markdown
# ShopEase

ShopEase is a deployment-focused e-commerce application developed as the
workload for a cloud and infrastructure deployment project.

The application provides realistic customer and administrator workflows,
including product browsing, authentication, wishlist, cart, checkout,
order placement, order lifecycle management, and administration.

## Purpose

The application was built to provide a realistic workload for experimenting
with and documenting different deployment and infrastructure approaches.

This branch provides the local-storage version of ShopEase for local
development, testing, and EC2 deployment practice.

## Technology Stack

- Python
- Flask
- HTML / CSS / JavaScript
- MySQL
- SQLAlchemy
- PyMySQL
- Local filesystem storage
- Git / GitHub
- k6 for traffic and load testing

## Application Documentation

For a detailed explanation of the application:

[Application Documentation](docs/application/PROJECT_DOCUMENTATION.md)

## Deployment Documentation

### Local Storage / EC2

The local-storage version can be deployed on an Ubuntu EC2 instance
using the guide below:

[Local Storage EC2 Deployment](docs/application/LOCAL_STORAGE_EC2_DEPLOYMENT.md)

### AWS RDS + S3

The RDS + S3 version is maintained separately in the `main` branch.

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
