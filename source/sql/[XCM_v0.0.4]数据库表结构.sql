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
-- Table structure for table `xcm_binance_kline_history`
--

DROP TABLE IF EXISTS `xcm_binance_kline_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_binance_kline_history` (
  `_id` bigint(20) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `base_asset` varchar(10) NOT NULL,
  `quote_asset` varchar(10) NOT NULL,
  `period` varchar(5) NOT NULL,
  `open_time` bigint(20) NOT NULL,
  `open` double NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `close` double NOT NULL,
  `volume` double NOT NULL,
  `close_time` bigint(20) NOT NULL,
  `quote_asset_volume` double NOT NULL,
  `num_of_trades` double NOT NULL,
  `buy_base_asset` double NOT NULL,
  `buy_quote_asset` double NOT NULL,
  `f_ignore` double NOT NULL,
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='币安历史K线表';
/*!40101 SET character_set_client = @saved_cs_client */;

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
-- Table structure for table `xcm_exchange_rate`
--

DROP TABLE IF EXISTS `xcm_exchange_rate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_exchange_rate` (
  `_id` int(11) NOT NULL AUTO_INCREMENT,
  `base_currency` varchar(10) NOT NULL,
  `quote_currency` varchar(10) NOT NULL,
  `rate` double NOT NULL,
  `create_time` int(11) NOT NULL,
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2931 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xcm_huobi_currency`
--

DROP TABLE IF EXISTS `xcm_huobi_currency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_huobi_currency` (
  `_id` int(11) NOT NULL AUTO_INCREMENT,
  `currency` varchar(20) NOT NULL COMMENT '名称',
  `full_name` varchar(100) DEFAULT NULL COMMENT '全名',
  `desc` varchar(500) DEFAULT NULL COMMENT '描述',
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB AUTO_INCREMENT=119 DEFAULT CHARSET=utf8 COMMENT='火币Pro币种表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xcm_huobi_kline`
--

DROP TABLE IF EXISTS `xcm_huobi_kline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_huobi_kline` (
  `_id` bigint(20) NOT NULL COMMENT '主键',
  `symbol` varchar(100) NOT NULL COMMENT '交易对',
  `period` varchar(10) DEFAULT NULL COMMENT 'K线周期',
  `ts` bigint(20) DEFAULT NULL COMMENT '获取时间',
  `id` int(11) DEFAULT NULL COMMENT 'kline id / K线时间戳',
  `amount` double DEFAULT NULL COMMENT '成交量',
  `count` double DEFAULT NULL COMMENT '成交笔数',
  `open` double DEFAULT NULL COMMENT '开盘价',
  `close` double DEFAULT NULL COMMENT '收盘价。\n当K线为最晚的一根时，是最新成交价。',
  `low` double DEFAULT NULL COMMENT '最低价',
  `high` double DEFAULT NULL COMMENT '最高价',
  `vol` double DEFAULT NULL COMMENT '成交额。\n即 sum（每一笔成交价 * 该笔的成交量）。',
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='火币Pro_K线表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xcm_huobi_kline_history`
--

DROP TABLE IF EXISTS `xcm_huobi_kline_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_huobi_kline_history` (
  `_id` bigint(20) NOT NULL COMMENT '主键',
  `symbol` varchar(100) NOT NULL COMMENT '交易对',
  `period` varchar(10) NOT NULL COMMENT 'K线周期',
  `id` int(11) NOT NULL COMMENT 'kline id / K线时间戳',
  `amount` double DEFAULT NULL COMMENT '成交量',
  `count` double DEFAULT NULL COMMENT '成交笔数',
  `open` double DEFAULT NULL COMMENT '开盘价',
  `close` double DEFAULT NULL COMMENT '收盘价。\n当K线为最晚的一根时，是最新成交价。',
  `low` double DEFAULT NULL COMMENT '最低价',
  `high` double DEFAULT NULL COMMENT '最高价',
  `vol` double DEFAULT NULL COMMENT '成交额。\n即 sum（每一笔成交价 * 该笔的成交量）。',
  PRIMARY KEY (`symbol`,`period`,`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='火币Pro历史K线表';
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
-- Table structure for table `xcm_okex_kline`
--

DROP TABLE IF EXISTS `xcm_okex_kline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_okex_kline` (
  `_id` bigint(20) NOT NULL,
  `symbol` varchar(20) NOT NULL COMMENT '交易对',
  `base_currency` varchar(20) NOT NULL COMMENT '交易币种',
  `quote_currency` varchar(20) NOT NULL COMMENT '计价币种',
  `period` varchar(10) NOT NULL COMMENT '周期',
  `open` double NOT NULL COMMENT '开盘价',
  `high` double NOT NULL COMMENT '最高价',
  `low` double NOT NULL COMMENT '最低价',
  `close` double NOT NULL COMMENT '收盘价',
  `timestamp` bigint(20) NOT NULL COMMENT '时间戳',
  `vol` double NOT NULL COMMENT '成交量',
  PRIMARY KEY (`_id`,`period`,`quote_currency`,`base_currency`,`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='OKEx_K线表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xcm_okex_kline_history`
--

DROP TABLE IF EXISTS `xcm_okex_kline_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_okex_kline_history` (
  `_id` bigint(20) NOT NULL,
  `symbol` varchar(20) NOT NULL COMMENT '交易对',
  `base_currency` varchar(20) NOT NULL COMMENT '交易币种',
  `quote_currency` varchar(20) NOT NULL COMMENT '计价币种',
  `period` varchar(10) NOT NULL COMMENT '周期',
  `open` double NOT NULL COMMENT '开盘价',
  `high` double NOT NULL COMMENT '最高价',
  `low` double NOT NULL COMMENT '最低价',
  `close` double NOT NULL COMMENT '收盘价',
  `timestamp` bigint(20) NOT NULL COMMENT '时间戳',
  `vol` double NOT NULL COMMENT '成交量',
  PRIMARY KEY (`timestamp`,`period`,`quote_currency`,`base_currency`,`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='OKEx历史K线表';
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

--
-- Table structure for table `xcm_okex_ticker`
--

DROP TABLE IF EXISTS `xcm_okex_ticker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_okex_ticker` (
  `_id` int(11) NOT NULL AUTO_INCREMENT,
  `symbol` varchar(20) NOT NULL COMMENT '交易对',
  `base_currency` varchar(20) NOT NULL COMMENT '交易币种',
  `quote_currency` varchar(20) NOT NULL COMMENT '计价币种',
  `buy` double NOT NULL COMMENT '买一价',
  `high` double NOT NULL COMMENT '最高价',
  `last` double NOT NULL COMMENT '最新成交价',
  `low` double NOT NULL COMMENT '最低价',
  `sell` double NOT NULL COMMENT '卖一价',
  `timestamp` bigint(20) NOT NULL COMMENT '时间戳',
  `vol` double NOT NULL COMMENT '成交量(最近的24小时)',
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB AUTO_INCREMENT=570 DEFAULT CHARSET=utf8 COMMENT='OKEx行情表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xcm_temp`
--

DROP TABLE IF EXISTS `xcm_temp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_temp` (
  `_id` bigint(20) NOT NULL,
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xcm_vxn_currency`
--

DROP TABLE IF EXISTS `xcm_vxn_currency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_vxn_currency` (
  `_id` int(11) NOT NULL AUTO_INCREMENT,
  `currency` varchar(20) NOT NULL,
  `fullname` varchar(50) NOT NULL,
  `cnname` varchar(4550) DEFAULT NULL,
  `description` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1307 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xcm_vxn_currency_info`
--

DROP TABLE IF EXISTS `xcm_vxn_currency_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xcm_vxn_currency_info` (
  `_id` int(11) NOT NULL AUTO_INCREMENT,
  `currency` varchar(20) NOT NULL COMMENT '币种',
  `fullname` varchar(50) NOT NULL COMMENT '币种全名',
  `cnname` varchar(50) NOT NULL COMMENT '币种中文名',
  `description` varchar(500) DEFAULT NULL COMMENT '币种描述',
  `price_cny` double DEFAULT NULL COMMENT '人民币价格',
  `price_scope` double DEFAULT NULL COMMENT '涨跌幅',
  `high` double DEFAULT NULL COMMENT '24H最高价',
  `low` double DEFAULT NULL COMMENT '24H最低价',
  `circulating_cny_value` double DEFAULT NULL COMMENT '人民币流通市值',
  `ranking` double DEFAULT NULL COMMENT '市值排名',
  `circulating_usd_value` double DEFAULT NULL COMMENT '美元市值',
  `circulating_btc_value` double DEFAULT NULL COMMENT 'btc市值',
  `circulating_value_percent` double DEFAULT NULL COMMENT '全球总市值百分比',
  `circulating_volume` double DEFAULT NULL COMMENT '流通量',
  `total_volume` double DEFAULT NULL COMMENT '总发行量',
  `circulating_rate` double DEFAULT NULL COMMENT '流通率',
  `turn_volume` double DEFAULT NULL COMMENT '24H成交额',
  `turn_volume_ranking` double DEFAULT NULL COMMENT '成交额排名',
  `turnover_rate` double DEFAULT NULL COMMENT '换手率',
  `create_time` int(11) DEFAULT NULL COMMENT '加入时间',
  `update_time` int(11) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1410 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-08-06  6:43:15
