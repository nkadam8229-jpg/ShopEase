-- MySQL dump 10.13  Distrib 8.4.10, for Linux (x86_64)
--
-- Host: localhost    Database: shopease
-- ------------------------------------------------------
-- Server version	8.4.10-0ubuntu0.26.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity_logs`
--

DROP TABLE IF EXISTS `activity_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_logs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `admin_id` bigint unsigned DEFAULT NULL,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_id` bigint unsigned DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_activity_logs_admin` (`admin_id`),
  KEY `idx_activity_logs_action` (`action`),
  KEY `idx_activity_logs_created` (`created_at`),
  CONSTRAINT `fk_activity_logs_admin` FOREIGN KEY (`admin_id`) REFERENCES `admins` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_logs`
--

LOCK TABLES `activity_logs` WRITE;
/*!40000 ALTER TABLE `activity_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `activity_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `addresses`
--

DROP TABLE IF EXISTS `addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addresses` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address_line` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `city` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `state` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pincode` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_default` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_addresses_user` (`user_id`),
  CONSTRAINT `fk_addresses_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addresses`
--

LOCK TABLES `addresses` WRITE;
/*!40000 ALTER TABLE `addresses` DISABLE KEYS */;
/*!40000 ALTER TABLE `addresses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('SUPER_ADMIN','ADMIN') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ADMIN',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_admins_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (1,'Nikhil Kadam','adminnikhil@gmail.com','scrypt:32768:8:1$0EsVfp8KLW2R3F2B$d3ded9bdadd8831d8e36b436de337cfacf468ee2ff2a7feeb2abbe6111504e80777e3b88538e9670317c55667caaa64d6e3e978f84cbc5bf18e6d16c042fe8ff','SUPER_ADMIN',1,'2026-08-11 09:15:39','2026-08-11 09:15:39');
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `banners`
--

DROP TABLE IF EXISTS `banners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banners` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `image_key` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `button_text` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `button_link` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `display_order` int unsigned NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_banners_active_order` (`is_active`,`display_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banners`
--

LOCK TABLES `banners` WRITE;
/*!40000 ALTER TABLE `banners` DISABLE KEYS */;
/*!40000 ALTER TABLE `banners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `brands`
--

DROP TABLE IF EXISTS `brands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `brands` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo_key` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brands`
--

LOCK TABLES `brands` WRITE;
/*!40000 ALTER TABLE `brands` DISABLE KEYS */;
INSERT INTO `brands` VALUES (1,'Samsung','samsung','brands/3ac5d44a89fe4e35ac1d33a35e3c6016.webp',1,'2026-08-11 10:23:44','2026-08-11 13:31:39'),(2,'Apple','apple','brands/049840add9b042b0b025842807e009f8.webp',1,'2026-08-11 10:23:51','2026-08-11 13:28:43'),(4,'Motorola','motorola','brands/c3db7ee4ee3b4575b623ea0ecfeef251.webp',1,'2026-08-11 13:38:10','2026-08-11 13:38:10'),(5,'U.S. POLO ASSN.','u.s.-polo-assn.','brands/b7b722b07b7941c081dcc2fb346aee53.webp',1,'2026-08-12 10:00:42','2026-08-12 10:00:42');
/*!40000 ALTER TABLE `brands` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_items` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `product_id` bigint unsigned NOT NULL,
  `product_size_id` bigint unsigned DEFAULT NULL,
  `quantity` int unsigned NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_cart_product` (`product_id`),
  KEY `idx_cart_user` (`user_id`),
  KEY `fk_cart_product_size` (`product_size_id`),
  CONSTRAINT `fk_cart_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cart_product_size` FOREIGN KEY (`product_size_id`) REFERENCES `product_sizes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cart_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_cart_quantity` CHECK ((`quantity` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
INSERT INTO `cart_items` VALUES (1,1,7,26,2,'2026-08-12 18:23:25','2026-08-12 18:52:14'),(2,1,3,NULL,2,'2026-08-12 18:35:36','2026-08-13 10:04:40'),(3,2,10,34,1,'2026-08-12 18:47:56','2026-08-12 18:47:56'),(4,2,10,35,1,'2026-08-12 18:50:13','2026-08-12 18:50:13'),(5,1,6,NULL,2,'2026-08-12 18:52:28','2026-08-12 18:52:32'),(6,1,9,20,1,'2026-08-12 18:52:49','2026-08-12 18:52:49'),(15,3,3,NULL,13,'2026-08-13 10:03:41','2026-08-13 10:04:40'),(16,3,3,NULL,16,'2026-08-13 10:03:47','2026-08-13 10:05:53'),(17,3,9,22,1,'2026-08-13 10:07:15','2026-08-13 10:07:15');
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `image_key` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Electronics','electronics','categories/4eb5ccbadf144ac3920d529dad736a8c.webp',1,'2026-08-11 09:44:53','2026-08-11 12:11:36'),(3,'Home Appliances','home-appliances','categories/55593efebfab4e808b574db9de7f686e.webp',1,'2026-08-11 11:51:05','2026-08-11 12:13:44'),(4,'Men\'s Clothing','men\'s-clothing','categories/f399173524594fd58d13ff792cd7850e.webp',1,'2026-08-11 13:03:40','2026-08-11 13:03:40'),(7,'Women\'s Clothing','women\'s-clothing','categories/8a3be6b9fd174a469b84cd6c02288d14.webp',1,'2026-08-11 16:42:03','2026-08-11 16:42:03');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `order_id` bigint unsigned NOT NULL,
  `product_id` bigint unsigned DEFAULT NULL,
  `product_size_id` bigint unsigned DEFAULT NULL,
  `product_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sku` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `variant_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `quantity` int unsigned NOT NULL,
  `unit_price` decimal(12,2) NOT NULL,
  `total_price` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_order_items_order` (`order_id`),
  KEY `idx_order_items_product` (`product_id`),
  KEY `fk_order_items_product_size` (`product_size_id`),
  CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_order_items_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_order_items_product_size` FOREIGN KEY (`product_size_id`) REFERENCES `product_sizes` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_order_items_price` CHECK ((`unit_price` >= 0)),
  CONSTRAINT `chk_order_items_quantity` CHECK ((`quantity` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `order_number` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  `total_amount` decimal(12,2) NOT NULL,
  `payment_method` enum('COD') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'COD',
  `status` enum('PENDING','CONFIRMED','PACKED','SHIPPED','DELIVERED','CANCELLED') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDING',
  `cancellation_requested` tinyint(1) NOT NULL DEFAULT '0',
  `cancellation_reason` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cancellation_requested_at` timestamp NULL DEFAULT NULL,
  `cancellation_approved_at` timestamp NULL DEFAULT NULL,
  `shipping_full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shipping_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shipping_address_line` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shipping_city` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shipping_state` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shipping_pincode` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_number` (`order_number`),
  KEY `idx_orders_user` (`user_id`),
  KEY `idx_orders_status` (`status`),
  KEY `idx_orders_created` (`created_at`),
  CONSTRAINT `fk_orders_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `chk_orders_subtotal` CHECK ((`subtotal` >= 0)),
  CONSTRAINT `chk_orders_total` CHECK ((`total_amount` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_images`
--

DROP TABLE IF EXISTS `product_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_images` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `product_id` bigint unsigned NOT NULL,
  `image_key` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `alt_text` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `display_order` int unsigned NOT NULL DEFAULT '0',
  `is_primary` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_product_images_product` (`product_id`),
  KEY `idx_product_images_order` (`product_id`,`display_order`),
  CONSTRAINT `fk_product_images_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_images`
--

LOCK TABLES `product_images` WRITE;
/*!40000 ALTER TABLE `product_images` DISABLE KEYS */;
INSERT INTO `product_images` VALUES (15,3,'products/6acaacba3e324df298ffe820d807c202.webp','Louis Philippe',0,1,'2026-08-11 17:37:07'),(16,3,'products/1d2d1af323864e0784cae800da5df33a.webp','Louis Philippe',1,0,'2026-08-11 17:37:07'),(17,5,'products/79f86a1541df4264a8114eef6129a0a1.webp','Samsung Galaxy Z Flip8 5G',0,1,'2026-08-11 18:12:19'),(18,5,'products/61033ecd5487491f91e26b638fcb0f09.webp','Samsung Galaxy Z Flip8 5G',1,0,'2026-08-11 18:12:19'),(19,5,'products/0bb903cfffac4359bd39505ce275636c.webp','Samsung Galaxy Z Flip8 5G',2,0,'2026-08-11 18:12:19'),(20,4,'products/b67e1ecf388748a59290710424c3afc3.webp','Motorola edge 70',0,1,'2026-08-12 13:40:37'),(21,4,'products/702f3452a7824f5187f062f5833c985e.webp','Motorola edge 70',1,0,'2026-08-12 13:40:37'),(22,4,'products/c87f7f263b21431fa99419f564357029.webp','Motorola edge 70',2,0,'2026-08-12 13:40:37'),(23,4,'products/259d07a9c18b45a59205acc3841c2cef.webp','Motorola edge 70',3,0,'2026-08-12 13:40:37'),(24,4,'products/88bace6c0a5a48bbae70a75924ffee74.webp','Motorola edge 70',4,0,'2026-08-12 13:40:37'),(25,4,'products/442272345579451c96e89afd43384b2d.webp','Motorola edge 70',5,0,'2026-08-12 13:40:37'),(26,4,'products/594b694ed11f4c83bbb706cd8ff09b66.webp','Motorola edge 70',6,0,'2026-08-12 13:40:37'),(27,7,'products/43a4503653574aea82c1d106101a9f35.webp','Apple iPhone 17 (black, 256gb)',0,1,'2026-08-12 13:41:17'),(28,7,'products/ed475cca8cbd4fbeaa792a3d690774b1.webp','Apple iPhone 17 (black, 256gb)',1,0,'2026-08-12 13:41:17'),(29,7,'products/0583a9e5a9e64feeb19d54120cc082c2.webp','Apple iPhone 17 (black, 256gb)',2,0,'2026-08-12 13:41:17'),(30,7,'products/7fcc2eaf4b8b408796029d888c970be4.webp','Apple iPhone 17 (black, 256gb)',3,0,'2026-08-12 13:41:17'),(31,8,'products/70aa4a860467433eac88411772e46a79.webp','Motorola edge 70 1TB',0,1,'2026-08-12 13:41:43'),(32,8,'products/f94e3974d8fd49a488ca29e825fd82ca.webp','Motorola edge 70 1TB',1,0,'2026-08-12 13:41:43'),(33,8,'products/793b77d9b7714a6faed62c7f187b34f7.webp','Motorola edge 70 1TB',2,0,'2026-08-12 13:41:43'),(34,8,'products/1a2e0f9a7e5545a79e9b716998c0879e.webp','Motorola edge 70 1TB',3,0,'2026-08-12 13:41:43'),(35,8,'products/ae8f3ada22a74a32b7d2852691799b22.webp','Motorola edge 70 1TB',4,0,'2026-08-12 13:41:43'),(36,8,'products/4b9be58fdbf1427cbf7fcfbf3f77b257.webp','Motorola edge 70 1TB',5,0,'2026-08-12 13:41:43'),(37,8,'products/315ab6f4377c41b3bd72905e086ddb4b.webp','Motorola edge 70 1TB',6,0,'2026-08-12 13:41:43'),(38,9,'products/9c3885d75cdf4e90b29890d835779881.webp','U.S. Polo Assn Men Polo T-Shirt',0,1,'2026-08-12 13:44:14'),(39,9,'products/9833cace1e4243aeb0baae46853cec7b.webp','U.S. Polo Assn Men Polo T-Shirt',1,0,'2026-08-12 13:44:14'),(40,9,'products/c0a8d3cd25014a7aa9e98cd579e15b3d.webp','U.S. Polo Assn Men Polo T-Shirt',2,0,'2026-08-12 13:44:14'),(41,6,'products/6f379c760c084c169c7c8295e817f221.webp','Urbano Fashion Men\'s Cotton Full Sleeve',0,1,'2026-08-12 13:44:36'),(42,6,'products/adb6664b34aa44f1b8228e2c943c7ee7.webp','Urbano Fashion Men\'s Cotton Full Sleeve',1,0,'2026-08-12 13:44:36'),(43,10,'products/a2569926107c465d9c372d87c23d0cda.webp','ASUS Vivobook Go 15 (2026)',0,1,'2026-08-12 16:34:02'),(44,10,'products/69c989a900e640f7bf13263d71b649d6.webp','ASUS Vivobook Go 15 (2026)',1,0,'2026-08-12 16:34:02'),(45,10,'products/9a0ffc64bc4c434b94e0d4a955516392.webp','ASUS Vivobook Go 15 (2026)',2,0,'2026-08-12 16:34:02'),(46,10,'products/88285ab35a9a47a3bc0d7fce76bf2f2b.webp','ASUS Vivobook Go 15 (2026)',3,0,'2026-08-12 16:34:02'),(47,10,'products/cf9ac623fa1e4ae9a93ebfc549562002.webp','ASUS Vivobook Go 15 (2026)',4,0,'2026-08-12 16:34:02');
/*!40000 ALTER TABLE `product_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_sizes`
--

DROP TABLE IF EXISTS `product_sizes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_sizes` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `product_id` bigint unsigned NOT NULL,
  `size` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` decimal(12,2) DEFAULT NULL,
  `quantity` int unsigned NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_product_size` (`product_id`,`size`),
  KEY `idx_product_sizes_product` (`product_id`),
  CONSTRAINT `fk_product_sizes_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_sizes`
--

LOCK TABLES `product_sizes` WRITE;
/*!40000 ALTER TABLE `product_sizes` DISABLE KEYS */;
INSERT INTO `product_sizes` VALUES (15,5,'256 GB',144999.00,100,'2026-08-12 09:57:39','2026-08-12 14:22:48'),(16,5,'512 GB',144999.00,100,'2026-08-12 09:57:39','2026-08-12 14:22:48'),(20,9,'S',1199.00,100,'2026-08-12 10:08:16','2026-08-12 14:22:48'),(21,9,'M',1199.00,180,'2026-08-12 10:08:16','2026-08-12 14:22:48'),(22,9,'L',1199.00,150,'2026-08-12 10:08:16','2026-08-12 14:22:48'),(25,7,'256 GB',84999.00,100,'2026-08-12 15:37:41','2026-08-12 15:37:41'),(26,7,'512 GB',91999.00,150,'2026-08-12 15:37:41','2026-08-12 15:37:41'),(34,10,'512GB/8GB',45999.00,50,'2026-08-12 17:36:31','2026-08-12 17:36:31'),(35,10,'1TB/16GB',51999.00,48,'2026-08-12 17:36:31','2026-08-12 17:36:31'),(36,3,'M',699.00,10,'2026-08-13 10:04:40','2026-08-13 10:04:40'),(37,3,'L',699.00,50,'2026-08-13 10:04:40','2026-08-13 10:04:40');
/*!40000 ALTER TABLE `product_sizes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_sizes_backup_20260812`
--

DROP TABLE IF EXISTS `product_sizes_backup_20260812`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_sizes_backup_20260812` (
  `id` bigint unsigned NOT NULL DEFAULT '0',
  `product_id` bigint unsigned NOT NULL,
  `size` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity` int unsigned NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_sizes_backup_20260812`
--

LOCK TABLES `product_sizes_backup_20260812` WRITE;
/*!40000 ALTER TABLE `product_sizes_backup_20260812` DISABLE KEYS */;
INSERT INTO `product_sizes_backup_20260812` VALUES (10,7,'256 GB',100,'2026-08-12 09:55:18','2026-08-12 09:55:18'),(11,7,'512 GB',150,'2026-08-12 09:55:18','2026-08-12 09:55:18'),(12,3,'M',50,'2026-08-12 09:55:31','2026-08-12 09:55:31'),(13,3,'L',50,'2026-08-12 09:55:31','2026-08-12 09:55:31'),(14,3,'XL',30,'2026-08-12 09:55:31','2026-08-12 09:55:31'),(15,5,'256 GB',100,'2026-08-12 09:57:39','2026-08-12 09:57:39'),(16,5,'512 GB',100,'2026-08-12 09:57:39','2026-08-12 09:57:39'),(20,9,'S',100,'2026-08-12 10:08:16','2026-08-12 10:08:16'),(21,9,'M',180,'2026-08-12 10:08:16','2026-08-12 10:08:16'),(22,9,'L',150,'2026-08-12 10:08:16','2026-08-12 10:08:16');
/*!40000 ALTER TABLE `product_sizes_backup_20260812` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `category_id` bigint unsigned NOT NULL,
  `subcategory_id` bigint unsigned DEFAULT NULL,
  `brand_id` bigint unsigned DEFAULT NULL,
  `sku` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(220) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `specifications` json DEFAULT NULL,
  `price` decimal(12,2) NOT NULL,
  `stock_quantity` int unsigned NOT NULL DEFAULT '0',
  `featured` tinyint(1) NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sku` (`sku`),
  UNIQUE KEY `slug` (`slug`),
  KEY `idx_products_category` (`category_id`),
  KEY `idx_products_subcategory` (`subcategory_id`),
  KEY `idx_products_brand` (`brand_id`),
  KEY `idx_products_price` (`price`),
  KEY `idx_products_stock` (`stock_quantity`),
  KEY `idx_products_featured` (`featured`),
  KEY `idx_products_active` (`is_active`),
  CONSTRAINT `fk_products_brand` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_products_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_products_subcategory` FOREIGN KEY (`subcategory_id`) REFERENCES `subcategories` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_products_price` CHECK ((`price` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (3,4,7,NULL,'PBA50032SE','Louis Philippe','louis-philippe','Soft cotton casul tshirt','{\"fit\": \"Slim\", \"size\": \"XXL\", \"type\": \"Polo Neck\", \"brand\": \"Louis Philippe Jeans\", \"fabric\": \"Pure Cotton\", \"sleeve\": \"Half Sleeve\", \"pack_of\": \"1\", \"pattern\": \"Solid\", \"brand_fit\": \"Regular Fit\", \"ideal_for\": \"Men\", \"neck_type\": \"Polo Neck\", \"style_code\": \"LRKPCSLFC86350\", \"suitable_for\": \"Western Wear\", \"sales_package\": \"1 T Shirt\"}',699.00,60,0,1,'2026-08-11 17:36:46','2026-08-13 10:04:40'),(4,1,8,4,'PBA50033SE','Motorola edge 70','motorola-edge-70','The MOTOROLA Edge 70 is a sleek smartphone with a 6.7-inch AMOLED display, Snapdragon 7 Gen 4 processor, 8GB RAM, and 256GB storage. It features 50MP cameras, a 5000mAh battery, 68W fast charging, and runs on Android 16.','{\"os\": \"Android 16\", \"ram\": \"8 GB\", \"sim\": \"Dual SIM\", \"brand\": \"MOTOROLA\", \"color\": \"PANTONE Bronze Green\", \"model\": \"Edge 70\", \"camera\": \"50MP + 50MP\", \"battery\": \"5000 mAh\", \"display\": \"6.7 inch Full HD+ AMOLED\", \"network\": \"5G\", \"storage\": \"256 GB\", \"charging\": \"68W TurboPower\", \"processor\": \"Snapdragon 7 Gen 4\", \"front_camera\": \"50MP\"}',27999.00,1000,0,1,'2026-08-11 17:46:06','2026-08-11 17:46:06'),(5,1,8,1,'PBA50034SE','Samsung Galaxy Z Flip8 5G','samsung-galaxy-z-flip8-5g','The Samsung Galaxy Z Flip8 5G features a 6.9-inch Dynamic AMOLED 2X display, Exynos 2600 processor, 12GB RAM, and 512GB storage. It comes with a 50MP + 12MP rear camera, 10MP front camera, 4300mAh battery, and runs on Android 17 with 5G connectivity.','{\"Ram\": \"12 GB\", \"Battery\": \"4300 mAH\", \"Display\": \"6.9 inch Dynamic AMOLED 2X Display\", \"Processor\": \"Exynos 2600\", \"Rear Camera\": \"50MP + 12MP\", \"Front Camera\": \"10MP\"}',144999.00,200,0,1,'2026-08-11 18:11:11','2026-08-12 09:57:39'),(6,4,6,NULL,'PBA80032SE','Urbano Fashion Men\'s Cotton Full Sleeve','urbano-fashion-men\'s-cotton-full-sleeve','This 100% cotton shirt features a solid pattern, regular fit, and long sleeves. It has a classic button-down, collared neck design and is made in India.','{\"fit\": \"Regular Fit\", \"care\": \"Machine Wash Cold\", \"wash\": \"Softener & Enzyme Wash\", \"brand\": \"Urbano Fashion\", \"collar\": \"Button-Down\", \"fabric\": \"Oxford\", \"weight\": \"300 g\", \"pattern\": \"Solid\", \"material\": \"100% Cotton\", \"quantity\": \"1 Shirt\"}',650.00,10,1,1,'2026-08-11 18:16:47','2026-08-13 09:56:08'),(7,1,8,2,'PBA51033SE','Apple iPhone 17 (black)','apple-iphone-17-(black)','Product Highlights\r\n\r\nThe iPhone 17 comes with 256 GB ROM and is powered by an A19 6-core processor with a 4.26 GHz clock speed. It features a 6.3-inch All-Screen OLED display for an immersive viewing experience. For photography, it offers a 48MP + 48MP dual rear camera setup and an 18MP front camera, making it suitable for high-quality photos, videos, and everyday use.','{\"OS\": \"iOS 26\", \"NFC\": \"true\", \"SIM\": \"Dual SIM\", \"USB\": \"USB-C 2.0\", \"Brand\": \"Apple\", \"Color\": \"Black\", \"Model\": \"iPhone 17\", \"Video\": \"Up to 4K Dolby Vision\", \"Weight\": \"177 g\", \"Battery\": \"Lithium Ion\", \"Display\": \"6.3-inch Super Retina XDR OLED\", \"Network\": \"5G / 4G / 3G / 2G\", \"Storage\": \"256 GB\", \"Bluetooth\": \"6.0\", \"Processor\": \"A19, Hexa Core, 4.26 GHz\", \"Dimensions\": \"149.6 x 71.5 x 7.95 mm\", \"Resolution\": \"2622 x 1206\", \"Rear Camera\": \"48MP + 48MP\", \"Front Camera\": \"18MP Center Stage\", \"Model Number\": \"MG6J4HN/A\", \"Refresh Rate\": \"Up to 120Hz ProMotion\", \"Fast Charging\": \"true\"}',84999.00,250,0,1,'2026-08-12 09:06:31','2026-08-12 15:37:41'),(8,1,8,4,'PBA50932SE','Motorola edge 70 1TB','motorola-edge-70-1tb','wejf ewoon [rnpner nnwepr n nw onorno','{\"ROM\": \"256 GB\", \"Battery\": \"5000 mAh\", \"Display\": \"6.7-inch Super HD pOLED Display | 120Hz\", \"Network\": \"5G\", \"Charging\": \"68W TurboPower Charging\", \"Processor\": \"Qualcomm Snapdragon 7 Gen 4 | Octa Core | Up to 2.8 GHz\", \"Rear Camera\": \"50MP + 50MP Dual Rear Camera\", \"Front Camera\": \"50MP\", \"Operating System\": \"Android 16\"}',32999.00,120,1,1,'2026-08-12 09:09:46','2026-08-12 09:09:46'),(9,4,7,5,'USPA-MEN-POLO-001','U.S. Polo Assn Men Polo T-Shirt','u.s.-polo-assn-men-polo-t-shirt','Classic men\'s polo T-shirt from U.S. Polo Assn., designed with a comfortable fit and stylish look. Suitable for casual wear and everyday use.','{\"Fit\": \"Regular Fit\", \"Neck\": \"Polo Collar\", \"Sleeve\": \"Half Sleeve\", \"Pattern\": \"Printed\", \"Material\": \"100% Cotton\", \"Wash Care\": \"Machine Wash\", \"Country of Origin\": \"India\"}',1199.00,430,0,1,'2026-08-12 10:07:49','2026-08-12 10:08:16'),(10,1,2,NULL,'ASUS-LAP-VIVO-001','ASUS Vivobook Go 15 (2026)','asus-vivobook-go-15-(2026)','ASUS Vivobook Go 15 is a lightweight 15.6-inch laptop powered by an AMD Ryzen 3 Quad Core processor with AMD Radeon graphics. It features a Full HD anti-glare display, Windows 11 Home, Wi-Fi 6E, Bluetooth 5.3, a 42Wh battery, and a 720p HD camera. With its slim design and 1.63 kg weight, it is suitable for everyday work, study, multitasking, travel, and entertainment.','{\"ram\": \"8 GB DDR5 & 16 GB DDR5\", \"type\": \"Thin and Light Laptop\", \"brand\": \"ASUS\", \"color\": \"Mixed Black\", \"model\": \"E1504FA-BQ2114WS\", \"ports\": \"1x USB 2.0 Type-A, 1x USB 3.2 Gen 1 Type-A, 1x USB 3.2 Gen 1 Type-C, 1x HDMI 1.4, Mic In\", \"camera\": \"720p HD with privacy shutter\", \"series\": \"Vivobook Go 15 (2026)\", \"weight\": \"1.63 kg\", \"battery\": \"42 Wh, 3-cell Li-ion\", \"display\": \"15.6-inch FHD (1920 x 1080) IPS-level Anti-glare, 60 Hz, 250 nits, 45% NTSC\", \"storage\": \"512 & 1TB GB M.2 NVMe PCIe 3.0 SSD\", \"graphics\": \"AMD Radeon\", \"keyboard\": \"Chiclet, non-backlit\", \"security\": \"Firmware TPM\", \"software\": \"MS Office 2024, Microsoft 365 Basic, Adobe Creative Cloud All Apps, McAfee 1 year\", \"processor\": \"AMD Ryzen 3 Quad Core, Variant 30, 4 Cores, Up to 4.1 GHz, 6 MB Cache\", \"dimensions\": \"360.3 x 232.5 x 17.9 mm\", \"box_contents\": \"Laptop, Power Adapter, User Guide, Warranty Documents\", \"connectivity\": \"Wi-Fi 6E, Bluetooth 5.3\", \"power_adapter\": \"45W\", \"operating_system\": \"Windows 11 Home\", \"special_features\": \"MIL-STD 810H, 84% screen-to-body ratio, Precision touchpad\"}',45999.00,98,0,1,'2026-08-12 15:11:14','2026-08-12 17:36:31');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recently_viewed`
--

DROP TABLE IF EXISTS `recently_viewed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recently_viewed` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `product_id` bigint unsigned NOT NULL,
  `viewed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_recently_viewed_user_product` (`user_id`,`product_id`),
  KEY `fk_recently_viewed_product` (`product_id`),
  KEY `idx_recently_viewed_user_date` (`user_id`,`viewed_at`),
  CONSTRAINT `fk_recently_viewed_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_recently_viewed_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recently_viewed`
--

LOCK TABLES `recently_viewed` WRITE;
/*!40000 ALTER TABLE `recently_viewed` DISABLE KEYS */;
/*!40000 ALTER TABLE `recently_viewed` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `settings` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `setting_value` text COLLATE utf8mb4_unicode_ci,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `setting_key` (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subcategories`
--

DROP TABLE IF EXISTS `subcategories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subcategories` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `category_id` bigint unsigned NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `image_key` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_subcategory_category_slug` (`category_id`,`slug`),
  KEY `idx_subcategories_category` (`category_id`),
  CONSTRAINT `fk_subcategories_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subcategories`
--

LOCK TABLES `subcategories` WRITE;
/*!40000 ALTER TABLE `subcategories` DISABLE KEYS */;
INSERT INTO `subcategories` VALUES (2,1,'Laptop','laptop','subcategories/5a278a2a9cdb43258a71d8ce64362d3b.webp',1,'2026-08-11 10:08:57','2026-08-11 12:32:54'),(5,1,'Headphoes','headphoes','subcategories/b7796bade7ac437880d7fa87fd5ea36d.webp',1,'2026-08-11 12:26:50','2026-08-11 12:26:50'),(6,4,'Shirts','shirts','subcategories/ba59cfb48a404db4b7c430e7761b0808.webp',1,'2026-08-11 16:42:32','2026-08-11 16:42:32'),(7,4,'T-Shirts','t-shirts','subcategories/39f23680d55644a3b4d1ad612bb54c65.webp',1,'2026-08-11 16:43:12','2026-08-11 17:43:39'),(8,1,'Phones','phones','subcategories/de52ad7f9ae54f109d8e7ca99250dd90.webp',1,'2026-08-11 17:30:07','2026-08-11 17:30:07');
/*!40000 ALTER TABLE `subcategories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone` (`phone`),
  KEY `idx_users_email` (`email`),
  KEY `idx_users_phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Test Customer','test@example.com','9876543210','scrypt:32768:8:1$htVjkKVvL1pN8aB6$ade3a159527cd39167018100270dbb2159e97598434bd7b4efa966dbbd19b5082189ee0e8e7fb1ee33151f233cd148224272b0eba76f9a560a6c334f2c070a82',1,'2026-08-11 09:02:12','2026-08-11 09:02:12'),(2,'Test Customer 2','test2@gmail.com','3929582332','scrypt:32768:8:1$4nvmjmUvl5WHYAyJ$4ccf41af615d609de3d2742ac2ce9d0de35c72f7a00ebbd5c1939ba65dab0df78d6eb579eacdffb1287eaefdd2858de1c97c34c214f6476b6e1552055c6b0745',1,'2026-08-12 11:06:29','2026-08-12 11:06:29'),(3,'test 3','test3@gmail.com','1342448423','scrypt:32768:8:1$Ez9DQOYtQX2bNDuR$5ecfcafdf780a6e8e923ce0dd81d44e25b2289a4683924fab0e498129c0273e69cf5bc76da1d09a6b2ba08166afbdcd8e135889485fd1923aea3a316cdc8aff1',1,'2026-08-13 08:58:54','2026-08-13 08:58:54');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlist`
--

DROP TABLE IF EXISTS `wishlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlist` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `product_id` bigint unsigned NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_wishlist_user_product` (`user_id`,`product_id`),
  KEY `fk_wishlist_product` (`product_id`),
  KEY `idx_wishlist_user` (`user_id`),
  CONSTRAINT `fk_wishlist_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wishlist_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlist`
--

LOCK TABLES `wishlist` WRITE;
/*!40000 ALTER TABLE `wishlist` DISABLE KEYS */;
/*!40000 ALTER TABLE `wishlist` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-13 10:57:38
