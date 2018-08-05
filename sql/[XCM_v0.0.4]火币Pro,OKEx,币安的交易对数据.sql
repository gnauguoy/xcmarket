-- MySQL dump 10.13  Distrib 5.7.17, for macos10.12 (x86_64)
--
-- Host: localhost    Database: xcmarket
-- ------------------------------------------------------
-- Server version	5.5.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `xcm_binance_symbol`
--

DROP TABLE IF EXISTS `xcm_binance_symbol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_binance_symbol` (
  `_id` int(11) NOT NULL AUTO_INCREMENT,
  `symbol` varchar(20) DEFAULT NULL COMMENT '交易对',
  `base_asset` varchar(20) DEFAULT NULL COMMENT '交易币种',
  `base_asset_precision` int(2) DEFAULT NULL COMMENT '交易货币精度',
  `quote_asset` varchar(20) DEFAULT NULL COMMENT '计价币种',
  `quote_asset_precision` int(2) DEFAULT NULL COMMENT '计价货币精度',
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB AUTO_INCREMENT=385 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xcm_huobi_symbol`
--

DROP TABLE IF EXISTS `xcm_huobi_symbol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_huobi_symbol` (
  `_id` int(11) NOT NULL AUTO_INCREMENT,
  `base_currency` varchar(20) NOT NULL COMMENT '基础币种',
  `quote_currency` varchar(20) NOT NULL COMMENT '计价币种',
  `price_precision` tinyint(2) NOT NULL COMMENT '价格精度位数（0为个位）',
  `amount_precision` tinyint(2) NOT NULL COMMENT '数量精度位数（0为个位）',
  `symbol` varchar(40) NOT NULL COMMENT '交易对',
  `symbol_partition` varchar(20) NOT NULL COMMENT '交易区。\nmain主区，innovation创新区，bifurcation分叉区。',
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB AUTO_INCREMENT=260 DEFAULT CHARSET=utf8 COMMENT='火币Pro交易对表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xcm_okex_symbol`
--

DROP TABLE IF EXISTS `xcm_okex_symbol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_okex_symbol` (
  `_id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL COMMENT '编号',
  `symbol` varchar(20) NOT NULL COMMENT '交易对',
  `base_min_size` double NOT NULL COMMENT '最小交易量',
  `base_increment` double NOT NULL COMMENT '交易货币精度',
  `quote_increment` double NOT NULL COMMENT '计价货币精度',
  `base_currency` varchar(20) NOT NULL COMMENT '交易币种',
  `quote_currency` varchar(20) NOT NULL COMMENT '计价币种',
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB AUTO_INCREMENT=570 DEFAULT CHARSET=utf8 COMMENT='OKEx交易对表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-08-06  6:45:33
