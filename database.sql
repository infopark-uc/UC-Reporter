-- --------------------------------------------------------
-- Хост:                         172.20.31.50
-- Версия сервера:               5.7.28-0ubuntu0.19.04.2 - (Ubuntu)
-- Операционная система:         Linux
-- HeidiSQL Версия:              10.3.0.5771
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Дамп структуры базы данных ucreporter
CREATE DATABASE IF NOT EXISTS `ucreporter` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin */;
USE `ucreporter`;

-- Дамп структуры для таблица ucreporter.cms_cdr_calllegs
CREATE TABLE IF NOT EXISTS `cms_cdr_calllegs` (
  `cms_node` mediumtext COLLATE utf8_bin,
  `callleg_id` text COLLATE utf8_bin,
  `date` text COLLATE utf8_bin,
  `call_id` text COLLATE utf8_bin,
  `VideoPacketLossPercentageRX` text COLLATE utf8_bin,
  `VideoPacketLossPercentageTX` text COLLATE utf8_bin,
  `AudioPacketLossPercentageRX` text COLLATE utf8_bin,
  `AudioPacketLossPercentageTX` text COLLATE utf8_bin,
  `AudioRoundTripTimeTX` text COLLATE utf8_bin,
  `VideoRoundTripTimeTX` text COLLATE utf8_bin
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица ucreporter.cms_cdr_calls
CREATE TABLE IF NOT EXISTS `cms_cdr_calls` (
  `StartTime` text COLLATE utf8_bin,
  `EndTime` text COLLATE utf8_bin,
  `id` text COLLATE utf8_bin,
  `coSpace` text COLLATE utf8_bin,
  `ownerName` text COLLATE utf8_bin,
  `callLegsCompleted` text COLLATE utf8_bin,
  `callLegsMaxActive` text COLLATE utf8_bin,
  `durationSeconds` text COLLATE utf8_bin,
  `name` text COLLATE utf8_bin,
  `cms_ip` mediumtext COLLATE utf8_bin
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица ucreporter.cms_cdr_records
CREATE TABLE IF NOT EXISTS `cms_cdr_records` (
  `date` text COLLATE utf8_bin,
  `startTime` text COLLATE utf8_bin,
  `endTime` text COLLATE utf8_bin,
  `session_id` text COLLATE utf8_bin,
  `callleg_id` text COLLATE utf8_bin,
  `sipcall_id` text COLLATE utf8_bin,
  `call_id` text COLLATE utf8_bin,
  `coSpace_id` text COLLATE utf8_bin,
  `coSpace_name` text COLLATE utf8_bin,
  `localAddress` text COLLATE utf8_bin,
  `remoteAddress` text COLLATE utf8_bin,
  `remoteParty` text COLLATE utf8_bin,
  `displayName` text COLLATE utf8_bin,
  `durationSeconds` text COLLATE utf8_bin,
  `reason` text COLLATE utf8_bin,
  `rxAudio_codec` text COLLATE utf8_bin,
  `txAudio_codec` text COLLATE utf8_bin,
  `rxAudio_packetLossBurst_duration` text COLLATE utf8_bin,
  `rxAudio_packetLossBurst_density` text COLLATE utf8_bin,
  `rxAudio_packetGap_duration` text COLLATE utf8_bin,
  `rxAudio_packetGap_density` text COLLATE utf8_bin,
  `rxVideo_codec` text COLLATE utf8_bin,
  `txVideo_codec` text COLLATE utf8_bin,
  `txVideo_maxHeight` text COLLATE utf8_bin,
  `txVideo_maxWidth` text COLLATE utf8_bin,
  `rxVideo_packetLossBurst_duration` text COLLATE utf8_bin,
  `rxVideo_packetLossBurst_density` text COLLATE utf8_bin,
  `rxVideo_packetGap_duration` text COLLATE utf8_bin,
  `rxVideo_packetGap_density` text COLLATE utf8_bin,
  `cms_ip` mediumtext COLLATE utf8_bin,
  `alarm_type` text COLLATE utf8_bin,
  `alarm_param` text COLLATE utf8_bin,
  `alarm_value` text COLLATE utf8_bin
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Table for CDR from CMS\r\n';

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица ucreporter.cms_servers
CREATE TABLE IF NOT EXISTS `cms_servers` (
  `id` int(11) DEFAULT NULL,
  `login` mediumtext COLLATE utf8_bin,
  `password` mediumtext COLLATE utf8_bin,
  `ip` mediumtext COLLATE utf8_bin,
  `api_port` mediumtext COLLATE utf8_bin,
  `cluster` mediumtext COLLATE utf8_bin
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица ucreporter.cm_phones_table
CREATE TABLE IF NOT EXISTS `cm_phones_table` (
  `phone_index` mediumtext COLLATE utf8_bin,
  `phone_number` mediumtext COLLATE utf8_bin,
  `phone_ip` mediumtext COLLATE utf8_bin,
  `phone_user` mediumtext COLLATE utf8_bin,
  `phone_password` mediumtext COLLATE utf8_bin
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица ucreporter.cm_roomsystems_table
CREATE TABLE IF NOT EXISTS `cm_roomsystems_table` (
  `room_index` int(11) DEFAULT NULL,
  `room_name` mediumtext COLLATE utf8_bin,
  `room_ip` mediumtext COLLATE utf8_bin,
  `room_user` mediumtext COLLATE utf8_bin,
  `room_password` mediumtext COLLATE utf8_bin
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица ucreporter.cm_servers_list
CREATE TABLE IF NOT EXISTS `cm_servers_list` (
  `cm_index` int(11) DEFAULT NULL,
  `cm_name` mediumtext COLLATE utf8_bin,
  `cm_ip` mediumtext COLLATE utf8_bin,
  `cm_username` mediumtext COLLATE utf8_bin,
  `cm_password` mediumtext COLLATE utf8_bin
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица ucreporter.server_config_table
CREATE TABLE IF NOT EXISTS `server_config_table` (
  `server_index` mediumtext COLLATE utf8_bin,
  `server_ip` mediumtext COLLATE utf8_bin,
  `server_port` mediumtext COLLATE utf8_bin
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Table from Phone http server';

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица ucreporter.widget_table
CREATE TABLE IF NOT EXISTS `widget_table` (
  `system_index` int(11) DEFAULT NULL,
  `widget_index` int(11) DEFAULT NULL,
  `widget_name` mediumtext COLLATE utf8_bin,
  `widget_data` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- Экспортируемые данные не выделены.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
