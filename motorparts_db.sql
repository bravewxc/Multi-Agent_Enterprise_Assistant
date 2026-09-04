/*
 Navicat Premium Data Transfer

 Source Server         : sdf
 Source Server Type    : MySQL
 Source Server Version : 80021
 Source Host           : localhost:3306
 Source Schema         : motorparts_db

 Target Server Type    : MySQL
 Target Server Version : 80021
 File Encoding         : 65001

 Date: 09/05/2026 20:09:35
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for customer
-- ----------------------------
DROP TABLE IF EXISTS `customer`;
CREATE TABLE `customer`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT '客户ID',
  `customer_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '客户编码',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '客户名称',
  `contact_person` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '联系人',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '联系电话',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '邮箱',
  `address` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '地址',
  `customer_type` tinyint(0) NULL DEFAULT 1 COMMENT '客户类型',
  `discount_level` tinyint(0) NULL DEFAULT 1 COMMENT '折扣等级',
  `registered_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '注册时间',
  `deleted` tinyint(0) NULL DEFAULT 0 COMMENT '删除标志',
  `create_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `update_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_customer_code`(`customer_code`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '客户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of customer
-- ----------------------------
INSERT INTO `customer` VALUES (1, 'CUS00001', '北京摩托车配件城', '张I', '13914001322', 'customer1@motorparts.com', '重庆市某区某街道1号', 2, 3, '2025-11-18 16:35:46', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (2, 'CUS00002', '上海汽配批发市场', '张O', '13942764996', 'customer2@motorparts.com', '重庆市某区某街道2号', 2, 4, '2024-06-23 08:54:22', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (3, 'CUS00003', '广州摩托车用品店', '张O', '13992931368', 'customer3@motorparts.com', '上海市某区某街道3号', 3, 4, '2024-12-02 21:57:18', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (4, 'CUS00004', '深圳骑士配件商行', '张K', '13943462642', 'customer4@motorparts.com', '深圳市某区某街道4号', 3, 4, '2024-04-27 14:55:43', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (5, 'CUS00005', '成都摩托之家', '张Q', '13939170172', 'customer5@motorparts.com', '重庆市某区某街道5号', 3, 2, '2024-01-27 03:16:53', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (6, 'CUS00006', '重庆摩托车批发中心', '张H', '13952565234', 'customer6@motorparts.com', '深圳市某区某街道6号', 1, 4, '2025-08-04 17:27:59', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (7, 'CUS00007', '杭州骑士装备店', '张P', '13935725510', 'customer7@motorparts.com', '重庆市某区某街道7号', 1, 2, '2024-09-21 11:50:14', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (8, 'CUS00008', '南京摩托车维修中心', '张X', '13941827483', 'customer8@motorparts.com', '广州市某区某街道8号', 1, 4, '2024-01-07 08:13:17', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (9, 'CUS00009', '武汉汽配超市', '张H', '13948844539', 'customer9@motorparts.com', '杭州市某区某街道9号', 1, 4, '2024-03-05 13:48:26', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (10, 'CUS00010', '西安摩托车配件商城', '张N', '13981525831', 'customer10@motorparts.com', '重庆市某区某街道10号', 2, 1, '2024-05-08 23:03:04', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (11, 'CUS00011', '天津摩托车市场', '张D', '13953305674', 'customer11@motorparts.com', '南京市某区某街道11号', 1, 2, '2025-10-26 05:28:56', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (12, 'CUS00012', '苏州骑士配件店', '张C', '13935217209', 'customer12@motorparts.com', '武汉市某区某街道12号', 3, 4, '2025-11-05 01:40:10', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (13, 'CUS00013', '青岛摩托车批发', '张N', '13991930263', 'customer13@motorparts.com', '北京市某区某街道13号', 2, 3, '2024-02-12 02:58:18', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (14, 'CUS00014', '大连摩托配件中心', '张J', '13940597533', 'customer14@motorparts.com', '深圳市某区某街道14号', 1, 1, '2024-05-27 10:51:44', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (15, 'CUS00015', '宁波摩托车城', '张E', '13933638165', 'customer15@motorparts.com', '杭州市某区某街道15号', 3, 3, '2024-04-25 19:32:53', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (16, 'CUS00016', '厦门骑士用品商行', '张M', '13942249657', 'customer16@motorparts.com', '重庆市某区某街道16号', 1, 1, '2025-06-24 14:26:29', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (17, 'CUS00017', '哈尔滨摩托配件', '张Q', '13931110053', 'customer17@motorparts.com', '武汉市某区某街道17号', 1, 4, '2024-12-10 06:33:24', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (18, 'CUS00018', '长春摩托车批发', '张Z', '13946447049', 'customer18@motorparts.com', '南京市某区某街道18号', 2, 1, '2025-05-21 11:35:49', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (19, 'CUS00019', '沈阳汽配中心', '张G', '13904795477', 'customer19@motorparts.com', '广州市某区某街道19号', 1, 1, '2024-12-07 15:10:39', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (20, 'CUS00020', '呼和浩特摩托城', '张H', '13960262500', 'customer20@motorparts.com', '重庆市某区某街道20号', 1, 2, '2024-07-25 22:22:59', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (21, 'CUS00021', '郑州摩托车配件', '张K', '13923722453', 'customer21@motorparts.com', '南京市某区某街道21号', 1, 3, '2025-12-04 15:22:25', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (22, 'CUS00022', '长沙骑士配件', '张N', '13949496102', 'customer22@motorparts.com', '杭州市某区某街道22号', 2, 1, '2025-08-03 11:13:04', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (23, 'CUS00023', '昆明摩托车用品', '张S', '13928650372', 'customer23@motorparts.com', '深圳市某区某街道23号', 3, 4, '2025-12-08 20:27:06', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (24, 'CUS00024', '南宁摩托批发', '张T', '13909143222', 'customer24@motorparts.com', '成都市某区某街道24号', 2, 2, '2024-10-09 11:39:44', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (25, 'CUS00025', '海口摩托车城', '张N', '13941263927', 'customer25@motorparts.com', '武汉市某区某街道25号', 1, 1, '2024-03-11 03:03:32', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (26, 'CUS00026', '贵阳骑士配件', '张A', '13997702709', 'customer26@motorparts.com', '西安市某区某街道26号', 1, 3, '2025-09-25 19:01:57', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (27, 'CUS00027', '拉萨摩托车中心', '张T', '13936277633', 'customer27@motorparts.com', '深圳市某区某街道27号', 3, 2, '2024-04-12 12:18:51', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (28, 'CUS00028', '兰州摩托用品', '张U', '13996786514', 'customer28@motorparts.com', '广州市某区某街道28号', 3, 1, '2025-07-17 16:41:16', 0, '2026-05-06 19:41:52', '2026-05-06 19:41:52');
INSERT INTO `customer` VALUES (29, 'CUS00029', '西宁摩托车批发', '张F', '13999573745', 'customer29@motorparts.com', '南京市某区某街道29号', 2, 4, '2025-01-28 04:05:21', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (30, 'CUS00030', '银川骑士配件', '张O', '13922322920', 'customer30@motorparts.com', '南京市某区某街道30号', 1, 2, '2025-07-28 03:12:42', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (31, 'CUS00031', '乌鲁木齐摩托城', '张C', '13972943953', 'customer31@motorparts.com', '北京市某区某街道31号', 1, 1, '2024-04-13 03:01:25', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (32, 'CUS00032', '太原摩托车配件', '张G', '13924454425', 'customer32@motorparts.com', '北京市某区某街道32号', 2, 1, '2025-01-28 23:24:11', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (33, 'CUS00033', '石家庄骑士用品', '张S', '13972600200', 'customer33@motorparts.com', '成都市某区某街道33号', 2, 4, '2025-06-06 15:47:02', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (34, 'CUS00034', '南昌摩托车中心', '张N', '13967715335', 'customer34@motorparts.com', '上海市某区某街道34号', 3, 3, '2025-01-06 09:02:01', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (35, 'CUS00035', '南宁摩托批发', '张Q', '13964096637', 'customer35@motorparts.com', '西安市某区某街道35号', 1, 1, '2025-08-09 17:12:57', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (36, 'CUS00036', '济南摩托车城', '张R', '13947180898', 'customer36@motorparts.com', '西安市某区某街道36号', 3, 4, '2025-11-13 07:08:48', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (37, 'CUS00037', '合肥骑士配件', '张M', '13956726481', 'customer37@motorparts.com', '广州市某区某街道37号', 3, 3, '2025-08-22 03:09:07', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (38, 'CUS00038', '福州摩托车用品', '张S', '13910130994', 'customer38@motorparts.com', '北京市某区某街道38号', 2, 2, '2025-01-21 16:03:35', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (39, 'CUS00039', '温州摩托车批发', '张R', '13990205712', 'customer39@motorparts.com', '重庆市某区某街道39号', 2, 1, '2025-03-01 22:26:15', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');
INSERT INTO `customer` VALUES (40, 'CUS00040', '无锡摩托配件', '张Y', '13946860107', 'customer40@motorparts.com', '上海市某区某街道40号', 1, 1, '2025-01-03 07:36:36', 0, '2026-05-06 19:41:53', '2026-05-06 19:41:53');

-- ----------------------------
-- Table structure for inventory
-- ----------------------------
DROP TABLE IF EXISTS `inventory`;
CREATE TABLE `inventory`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT '库存ID',
  `part_id` bigint(0) NOT NULL COMMENT '零部件ID',
  `current_quantity` int(0) NOT NULL DEFAULT 0 COMMENT '当前库存数量',
  `safety_stock` int(0) NULL DEFAULT 10 COMMENT '安全库存量',
  `last_inbound_time` datetime(0) NULL DEFAULT NULL COMMENT '最近入库时间',
  `last_outbound_time` datetime(0) NULL DEFAULT NULL COMMENT '最近出库时间',
  `warehouse_location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'A区-1号库' COMMENT '仓库位置',
  `deleted` tinyint(0) NULL DEFAULT 0 COMMENT '删除标志',
  `create_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `update_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_part_id`(`part_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 68 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '库存表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of inventory
-- ----------------------------
INSERT INTO `inventory` VALUES (1, 1, 104, 25, '2024-01-24 07:30:02', NULL, 'B区-1号库', 0, '2025-05-27 15:15:06', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (2, 2, 85, 22, '2024-10-13 10:43:51', NULL, 'B区-1号库', 0, '2024-08-27 09:08:46', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (3, 3, 9, 15, '2024-01-27 21:33:06', NULL, 'B区-1号库', 0, '2025-04-25 20:53:41', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (4, 4, 101, 12, '2025-09-14 17:20:42', NULL, 'B区-1号库', 0, '2024-07-02 13:32:12', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (5, 5, 29, 10, '2025-01-25 03:36:16', NULL, 'B区-1号库', 0, '2024-03-10 05:48:12', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (6, 6, 91, 29, '2025-11-21 17:57:45', NULL, 'B区-1号库', 0, '2025-09-04 04:33:38', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (7, 7, 6, 29, '2025-08-17 07:49:46', NULL, 'B区-1号库', 0, '2024-12-02 07:26:54', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (8, 8, 110, 12, '2024-04-02 15:36:38', NULL, 'B区-1号库', 0, '2024-04-23 16:04:07', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (9, 9, 119, 28, '2024-09-18 23:10:52', NULL, 'B区-1号库', 0, '2025-06-14 05:09:51', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (10, 10, 0, 19, '2024-02-04 00:09:27', NULL, 'B区-1号库', 0, '2024-05-20 11:05:55', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (11, 11, 93, 28, '2025-08-14 23:37:58', NULL, 'B区-1号库', 0, '2025-12-07 14:55:10', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (12, 12, 112, 20, '2024-04-05 04:13:55', NULL, 'B区-1号库', 0, '2025-04-13 16:26:09', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (13, 13, 6, 11, '2024-06-04 05:56:36', NULL, 'A区-2号库', 0, '2025-08-14 23:01:23', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (14, 14, 60, 22, '2024-01-05 14:21:03', NULL, 'A区-2号库', 0, '2024-07-19 07:44:55', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (15, 15, 78, 23, '2025-10-14 12:29:18', NULL, 'A区-2号库', 0, '2025-09-21 17:29:33', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (16, 16, 3, 20, '2024-03-13 12:41:07', NULL, 'A区-2号库', 0, '2025-02-14 21:56:31', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (17, 17, 88, 21, '2024-05-11 11:24:37', NULL, 'A区-2号库', 0, '2025-05-19 08:40:20', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (18, 18, 3, 27, '2025-04-15 06:54:41', NULL, 'A区-2号库', 0, '2024-04-08 21:59:57', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (19, 19, 1, 13, '2025-12-22 17:37:46', NULL, 'A区-2号库', 0, '2024-02-28 17:02:57', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (20, 20, 35, 26, '2025-05-07 06:39:11', NULL, 'A区-2号库', 0, '2025-02-13 14:51:20', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (21, 21, 102, 29, '2024-01-17 16:29:34', NULL, 'A区-2号库', 0, '2025-04-16 06:43:44', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (22, 22, 67, 11, '2025-02-22 12:12:29', NULL, 'A区-2号库', 0, '2024-06-24 11:26:46', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (23, 23, 34, 26, '2024-04-09 03:24:11', NULL, 'B区-2号库', 0, '2025-11-05 15:11:23', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (24, 24, 115, 17, '2024-01-02 19:04:17', NULL, 'B区-2号库', 0, '2025-06-24 17:29:49', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (25, 25, 35, 15, '2024-12-09 04:08:15', NULL, 'B区-2号库', 0, '2025-03-24 23:58:09', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (26, 26, 13, 22, '2025-07-17 04:45:42', NULL, 'B区-2号库', 0, '2025-02-19 09:35:12', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (27, 27, 12, 18, '2025-11-03 06:49:07', NULL, 'B区-2号库', 0, '2025-02-04 01:55:40', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (28, 28, 124, 29, '2024-05-07 21:07:04', NULL, 'B区-2号库', 0, '2025-04-16 02:08:48', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (29, 29, 16, 15, '2024-02-23 04:57:55', NULL, 'B区-2号库', 0, '2024-10-10 06:45:44', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (30, 30, 31, 27, '2024-12-20 07:45:11', NULL, 'B区-2号库', 0, '2024-03-28 09:36:39', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (31, 31, 98, 24, '2025-06-08 13:00:25', NULL, 'B区-2号库', 0, '2025-12-09 05:28:09', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (32, 32, 18, 25, '2024-04-12 10:37:48', NULL, 'B区-2号库', 0, '2025-04-21 15:50:58', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (33, 33, 53, 20, '2025-09-05 04:45:59', NULL, 'B区-2号库', 0, '2025-01-26 23:21:21', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (34, 34, 120, 24, '2024-03-02 22:10:01', NULL, 'B区-2号库', 0, '2024-05-23 07:58:07', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (35, 35, 12, 17, '2025-01-13 07:12:03', NULL, 'A区-2号库', 0, '2025-09-18 20:27:40', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (36, 36, 2, 24, '2024-06-07 07:23:12', NULL, 'A区-2号库', 0, '2024-03-17 19:40:17', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (37, 37, 77, 17, '2024-04-03 04:23:13', NULL, 'A区-2号库', 0, '2025-06-24 22:54:41', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (38, 38, 93, 24, '2025-12-14 04:40:11', NULL, 'A区-2号库', 0, '2024-04-13 02:31:14', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (39, 39, 67, 15, '2025-04-12 19:49:36', NULL, 'A区-2号库', 0, '2025-10-17 09:27:22', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (40, 40, 10, 16, '2025-04-26 22:33:23', NULL, 'A区-2号库', 0, '2025-06-17 08:37:07', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (41, 41, 92, 22, '2024-05-18 21:26:31', NULL, 'A区-2号库', 0, '2024-05-11 21:07:23', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (42, 42, 2, 26, '2024-10-12 01:44:03', NULL, 'A区-2号库', 0, '2024-07-13 18:36:43', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (43, 43, 29, 21, '2024-10-14 06:38:38', NULL, 'A区-2号库', 0, '2025-02-05 09:13:27', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (44, 44, 75, 21, '2024-06-28 17:04:44', NULL, 'A区-2号库', 0, '2025-05-13 12:50:50', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (45, 45, 53, 16, '2024-08-11 09:09:54', NULL, 'A区-1号库', 0, '2024-01-26 04:34:48', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (46, 46, 89, 13, '2024-01-28 19:44:35', NULL, 'A区-1号库', 0, '2025-05-16 09:35:12', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (47, 47, 1, 17, '2025-02-22 08:22:02', NULL, 'A区-1号库', 0, '2025-06-21 17:39:38', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (48, 48, 73, 13, '2024-12-19 21:10:22', NULL, 'A区-1号库', 0, '2025-05-03 14:11:07', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (49, 49, 52, 19, '2025-02-28 07:40:40', NULL, 'A区-1号库', 0, '2025-12-21 23:51:32', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (50, 50, 10, 18, '2024-10-28 03:44:41', NULL, 'A区-1号库', 0, '2025-08-12 19:08:37', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (51, 51, 97, 24, '2024-05-18 12:33:08', NULL, 'A区-1号库', 0, '2024-05-02 11:13:06', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (52, 52, 4, 22, '2024-09-23 08:16:33', NULL, 'A区-1号库', 0, '2024-11-23 15:01:51', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (53, 53, 13, 14, '2024-04-07 05:12:51', NULL, 'A区-1号库', 0, '2024-03-11 20:37:35', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (54, 54, 80, 26, '2025-02-22 15:37:16', NULL, 'A区-1号库', 0, '2025-02-03 22:49:20', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (55, 55, 33, 13, '2025-10-16 13:07:52', NULL, 'B区-2号库', 0, '2024-02-20 10:13:11', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (56, 56, 15, 21, '2025-04-16 04:58:04', NULL, 'B区-2号库', 0, '2024-11-11 01:40:06', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (57, 57, 79, 19, '2024-09-13 20:49:28', NULL, 'B区-2号库', 0, '2025-05-24 10:42:21', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (58, 58, 93, 14, '2024-04-10 10:43:13', NULL, 'B区-2号库', 0, '2025-03-04 03:00:47', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (59, 59, 78, 29, '2024-08-13 11:06:13', NULL, 'B区-2号库', 0, '2025-05-07 18:01:36', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (60, 60, 8, 25, '2024-07-02 18:08:58', NULL, 'B区-2号库', 0, '2025-03-11 20:26:15', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (61, 61, 94, 25, '2024-12-23 00:32:02', NULL, 'B区-2号库', 0, '2025-03-02 20:21:07', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (62, 62, 60, 20, '2024-03-10 22:09:19', NULL, 'B区-2号库', 0, '2024-02-19 03:11:10', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (63, 63, 45, 13, '2024-05-04 12:59:21', NULL, 'B区-2号库', 0, '2024-02-21 17:36:39', '2026-05-06 19:41:53');
INSERT INTO `inventory` VALUES (64, 64, 91, 17, '2024-06-23 09:33:42', NULL, 'B区-2号库', 0, '2025-01-08 04:05:06', '2026-05-06 19:41:54');
INSERT INTO `inventory` VALUES (65, 65, 111, 10, '2026-05-09 12:30:36', NULL, 'C区-3号库', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `inventory` VALUES (66, 66, 185, 10, '2026-05-09 12:30:36', NULL, 'C区-3号库', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `inventory` VALUES (67, 67, 186, 10, '2026-05-09 12:30:36', NULL, 'C区-3号库', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');

-- ----------------------------
-- Table structure for logistics
-- ----------------------------
DROP TABLE IF EXISTS `logistics`;
CREATE TABLE `logistics`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT '物流ID',
  `order_id` bigint(0) NOT NULL COMMENT '订单ID',
  `logistics_company` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '物流公司',
  `tracking_number` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '运单号',
  `ship_time` datetime(0) NULL DEFAULT NULL COMMENT '发货时间',
  `estimated_arrival_time` datetime(0) NULL DEFAULT NULL COMMENT '预计到达时间',
  `actual_arrival_time` datetime(0) NULL DEFAULT NULL COMMENT '实际到达时间',
  `status` tinyint(0) NULL DEFAULT 1 COMMENT '物流状态',
  `receiver` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '收货人',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '备注',
  `deleted` tinyint(0) NULL DEFAULT 0 COMMENT '删除标志',
  `create_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `update_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_order_id`(`order_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 79 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '物流信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of logistics
-- ----------------------------
INSERT INTO `logistics` VALUES (1, 1, '佳吉快运', 'SF13785854', '2025-12-27 22:18:37', '2026-01-01 22:18:37', '2026-01-02 22:18:37', 3, '收货员D', NULL, 0, '2025-12-27 22:18:37', '2026-05-06 19:42:09');
INSERT INTO `logistics` VALUES (2, 2, '佳吉快运', 'YT92420127', '2025-04-04 07:59:21', '2025-04-09 07:59:21', '2025-04-10 07:59:21', 3, '收货员D', NULL, 0, '2025-04-04 07:59:21', '2026-05-06 19:42:09');
INSERT INTO `logistics` VALUES (3, 4, '中通快递', 'SF12657287', '2024-10-22 12:12:30', '2024-10-28 12:12:30', NULL, 2, '收货员V', NULL, 0, '2024-10-22 12:12:30', '2026-05-06 19:42:09');
INSERT INTO `logistics` VALUES (4, 8, '百世快运', 'YT67328701', '2024-02-05 19:08:47', '2024-02-08 19:08:47', NULL, 2, '收货员Z', NULL, 0, '2024-02-05 19:08:47', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (5, 9, '百世快运', 'SF25667052', '2025-06-21 19:10:09', '2025-06-25 19:10:09', '2025-06-25 19:10:09', 3, '收货员Y', NULL, 0, '2025-06-21 19:10:09', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (6, 15, '韵达快递', 'SF84090345', '2025-08-25 18:23:24', '2025-09-01 18:23:24', NULL, 2, '收货员G', NULL, 0, '2025-08-25 18:23:24', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (7, 16, '佳吉快运', 'YT20788002', '2024-01-26 02:51:20', '2024-02-01 02:51:20', NULL, 2, '收货员S', NULL, 0, '2024-01-26 02:51:20', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (8, 17, '天地华宇', 'YT41575046', '2025-12-12 10:11:41', '2025-12-19 10:11:41', NULL, 2, '收货员G', NULL, 0, '2025-12-12 10:11:41', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (9, 19, '天地华宇', 'YT67667015', '2025-07-13 04:15:48', '2025-07-17 04:15:48', NULL, 2, '收货员Q', NULL, 0, '2025-07-13 04:15:48', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (10, 21, '顺丰速运', 'SF13178235', '2025-10-11 07:54:48', '2025-10-17 07:54:48', '2025-10-17 07:54:48', 3, '收货员Q', NULL, 0, '2025-10-11 07:54:48', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (11, 23, '顺丰速运', 'YT69882714', '2024-08-29 15:41:32', '2024-09-05 15:41:32', NULL, 2, '收货员L', NULL, 0, '2024-08-29 15:41:32', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (12, 24, '申通快递', 'YT87777876', '2024-05-18 13:55:09', '2024-05-23 13:55:09', NULL, 2, '收货员K', NULL, 0, '2024-05-18 13:55:09', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (13, 27, '佳吉快运', 'YT63689639', '2024-12-12 02:22:26', '2024-12-15 02:22:26', NULL, 2, '收货员Q', NULL, 0, '2024-12-12 02:22:26', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (14, 29, '安能物流', 'YT20166348', '2024-02-19 07:52:54', '2024-02-23 07:52:54', '2024-02-22 07:52:54', 3, '收货员I', NULL, 0, '2024-02-19 07:52:54', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (15, 31, '申通快递', 'YT61475098', '2024-07-03 04:06:58', '2024-07-09 04:06:58', '2024-07-10 04:06:58', 3, '收货员I', NULL, 0, '2024-07-03 04:06:58', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (16, 32, '顺丰速运', 'YT98540860', '2025-11-10 07:21:39', '2025-11-15 07:21:39', '2025-11-14 07:21:39', 3, '收货员Q', NULL, 0, '2025-11-10 07:21:39', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (17, 33, '顺丰速运', 'SF71768172', '2025-01-16 11:53:19', '2025-01-21 11:53:19', NULL, 2, '收货员U', NULL, 0, '2025-01-16 11:53:19', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (18, 34, '德邦物流', 'YT76598966', '2024-02-13 02:31:26', '2024-02-16 02:31:26', '2024-02-16 02:31:26', 3, '收货员O', NULL, 0, '2024-02-13 02:31:26', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (19, 35, '德邦物流', 'YT21483659', '2025-01-21 17:07:39', '2025-01-27 17:07:39', '2025-01-26 17:07:39', 3, '收货员F', NULL, 0, '2025-01-21 17:07:39', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (20, 36, '德邦物流', 'YT43754750', '2024-03-16 05:21:43', '2024-03-19 05:21:43', NULL, 2, '收货员R', NULL, 0, '2024-03-16 05:21:43', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (21, 37, '顺丰速运', 'YT46736878', '2025-03-23 02:21:07', '2025-03-27 02:21:07', '2025-03-26 02:21:07', 3, '收货员M', NULL, 0, '2025-03-23 02:21:07', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (22, 38, '顺丰速运', 'SF97204007', '2024-03-10 02:23:00', '2024-03-14 02:23:00', '2024-03-15 02:23:00', 3, '收货员M', NULL, 0, '2024-03-10 02:23:00', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (23, 39, '百世快运', 'SF46062213', '2025-12-28 19:23:28', '2025-12-31 19:23:28', NULL, 2, '收货员P', NULL, 0, '2025-12-28 19:23:28', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (24, 40, '天地华宇', 'YT52324804', '2025-01-28 22:07:28', '2025-02-01 22:07:28', NULL, 2, '收货员Y', NULL, 0, '2025-01-28 22:07:28', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (25, 41, '韵达快递', 'YT223100', '2025-12-18 16:54:25', '2025-12-23 16:54:25', '2025-12-23 16:54:25', 3, '收货员W', NULL, 0, '2025-12-18 16:54:25', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (26, 42, '安能物流', 'SF33742850', '2024-12-24 02:56:26', '2024-12-29 02:56:26', '2024-12-28 02:56:26', 3, '收货员S', NULL, 0, '2024-12-24 02:56:26', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (27, 44, '中通快递', 'YT81834511', '2025-01-03 07:59:42', '2025-01-09 07:59:42', NULL, 2, '收货员X', NULL, 0, '2025-01-03 07:59:42', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (28, 46, '佳吉快运', 'YT33734379', '2025-09-19 16:15:03', '2025-09-24 16:15:03', NULL, 2, '收货员K', NULL, 0, '2025-09-19 16:15:03', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (29, 48, '韵达快递', 'YT56294887', '2024-11-05 04:31:14', '2024-11-11 04:31:14', NULL, 2, '收货员S', NULL, 0, '2024-11-05 04:31:14', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (30, 49, '德邦物流', 'SF87869317', '2024-08-04 09:59:49', '2024-08-10 09:59:49', NULL, 2, '收货员B', NULL, 0, '2024-08-04 09:59:49', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (31, 51, '韵达快递', 'YT46629057', '2025-08-09 07:51:55', '2025-08-16 07:51:55', NULL, 2, '收货员Q', NULL, 0, '2025-08-09 07:51:55', '2026-05-06 19:42:10');
INSERT INTO `logistics` VALUES (32, 52, '百世快运', 'SF81064918', '2025-04-14 02:15:19', '2025-04-18 02:15:19', NULL, 2, '收货员A', NULL, 0, '2025-04-14 02:15:19', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (33, 53, '德邦物流', 'SF73453004', '2025-06-29 05:46:54', '2025-07-05 05:46:54', '2025-07-05 05:46:54', 3, '收货员M', NULL, 0, '2025-06-29 05:46:54', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (34, 54, '申通快递', 'SF23262398', '2025-04-06 09:08:44', '2025-04-12 09:08:44', '2025-04-11 09:08:44', 3, '收货员C', NULL, 0, '2025-04-06 09:08:44', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (35, 55, '中通快递', 'YT44591627', '2024-04-22 02:47:52', '2024-04-26 02:47:52', NULL, 2, '收货员R', NULL, 0, '2024-04-22 02:47:52', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (36, 57, '圆通速递', 'SF63044741', '2025-05-16 05:55:26', '2025-05-21 05:55:26', '2025-05-21 05:55:26', 3, '收货员S', NULL, 0, '2025-05-16 05:55:26', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (37, 58, '圆通速递', 'SF26397151', '2025-05-16 18:35:35', '2025-05-21 18:35:35', NULL, 2, '收货员A', NULL, 0, '2025-05-16 18:35:35', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (38, 59, '百世快运', 'YT47978616', '2024-08-21 19:32:40', '2024-08-27 19:32:40', '2024-08-26 19:32:40', 3, '收货员G', NULL, 0, '2024-08-21 19:32:40', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (39, 60, '德邦物流', 'YT30062683', '2024-06-18 10:38:35', '2024-06-22 10:38:35', '2024-06-23 10:38:35', 3, '收货员C', NULL, 0, '2024-06-18 10:38:35', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (40, 62, '天地华宇', 'YT21054898', '2024-10-23 13:23:24', '2024-10-30 13:23:24', NULL, 2, '收货员E', NULL, 0, '2024-10-23 13:23:24', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (41, 63, '顺丰速运', 'SF28520745', '2024-06-06 17:22:07', '2024-06-09 17:22:07', NULL, 2, '收货员V', NULL, 0, '2024-06-06 17:22:07', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (42, 64, '佳吉快运', 'SF86141789', '2025-01-06 01:10:11', '2025-01-09 01:10:11', NULL, 2, '收货员R', NULL, 0, '2025-01-06 01:10:11', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (43, 66, '安能物流', 'YT46364446', '2025-11-05 10:34:51', '2025-11-11 10:34:51', NULL, 2, '收货员C', NULL, 0, '2025-11-05 10:34:51', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (44, 68, '圆通速递', 'YT81018971', '2025-08-28 19:09:11', '2025-08-31 19:09:11', '2025-09-01 19:09:11', 3, '收货员X', NULL, 0, '2025-08-28 19:09:11', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (45, 70, '韵达快递', 'YT21857626', '2025-12-08 05:04:53', '2025-12-13 05:04:53', '2025-12-12 05:04:53', 3, '收货员T', NULL, 0, '2025-12-08 05:04:53', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (46, 71, '圆通速递', 'YT61907159', '2024-07-26 16:08:27', '2024-07-29 16:08:27', '2024-07-30 16:08:27', 3, '收货员K', NULL, 0, '2024-07-26 16:08:27', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (47, 74, '顺丰速运', 'YT21395220', '2025-06-30 10:20:50', '2025-07-04 10:20:50', NULL, 2, '收货员H', NULL, 0, '2025-06-30 10:20:50', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (48, 76, '申通快递', 'SF91903647', '2024-06-21 06:21:28', '2024-06-24 06:21:28', NULL, 2, '收货员O', NULL, 0, '2024-06-21 06:21:28', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (49, 77, '德邦物流', 'YT28319934', '2024-01-25 02:15:07', '2024-01-30 02:15:07', NULL, 2, '收货员U', NULL, 0, '2024-01-25 02:15:07', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (50, 78, '百世快运', 'YT49733498', '2024-11-02 07:21:52', '2024-11-06 07:21:52', '2024-11-05 07:21:52', 3, '收货员R', NULL, 0, '2024-11-02 07:21:52', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (51, 80, '天地华宇', 'YT73718379', '2025-02-18 22:20:22', '2025-02-25 22:20:22', NULL, 2, '收货员C', NULL, 0, '2025-02-18 22:20:22', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (52, 81, '安能物流', 'YT13331785', '2024-10-25 17:13:57', '2024-10-29 17:13:57', '2024-10-28 17:13:57', 3, '收货员L', NULL, 0, '2024-10-25 17:13:57', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (53, 82, '韵达快递', 'SF57082114', '2025-09-20 17:24:15', '2025-09-25 17:24:15', '2025-09-26 17:24:15', 3, '收货员U', NULL, 0, '2025-09-20 17:24:15', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (54, 83, '百世快运', 'SF44837095', '2024-05-28 03:16:05', '2024-06-02 03:16:05', NULL, 2, '收货员S', NULL, 0, '2024-05-28 03:16:05', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (55, 84, '德邦物流', 'YT94836753', '2024-06-28 09:10:47', '2024-07-04 09:10:47', '2024-07-05 09:10:47', 3, '收货员S', NULL, 0, '2024-06-28 09:10:47', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (56, 86, '韵达快递', 'YT39738852', '2025-11-14 21:33:36', '2025-11-19 21:33:36', '2025-11-19 21:33:36', 3, '收货员R', NULL, 0, '2025-11-14 21:33:36', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (57, 88, '安能物流', 'SF68431914', '2025-02-10 21:51:10', '2025-02-17 21:51:10', NULL, 2, '收货员R', NULL, 0, '2025-02-10 21:51:10', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (58, 89, '韵达快递', 'SF76984399', '2025-05-11 22:10:47', '2025-05-18 22:10:47', NULL, 2, '收货员R', NULL, 0, '2025-05-11 22:10:47', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (59, 90, '中通快递', 'SF18795', '2025-09-13 17:55:27', '2025-09-17 17:55:27', '2025-09-18 17:55:27', 3, '收货员Q', NULL, 0, '2025-09-13 17:55:27', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (60, 92, '韵达快递', 'SF60641011', '2024-04-10 08:03:53', '2024-04-13 08:03:53', NULL, 2, '收货员M', NULL, 0, '2024-04-10 08:03:53', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (61, 95, '安能物流', 'SF86678214', '2025-05-16 00:28:15', '2025-05-21 00:28:15', NULL, 2, '收货员P', NULL, 0, '2025-05-16 00:28:15', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (62, 97, '申通快递', 'SF50946791', '2024-09-09 14:46:55', '2024-09-12 14:46:55', '2024-09-13 14:46:55', 3, '收货员B', NULL, 0, '2024-09-09 14:46:55', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (63, 99, '中通快递', 'SF93331314', '2025-12-04 05:00:05', '2025-12-07 05:00:05', '2025-12-08 05:00:05', 3, '收货员I', NULL, 0, '2025-12-04 05:00:05', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (64, 100, '天地华宇', 'SF66579140', '2024-08-21 21:44:36', '2024-08-25 21:44:36', '2024-08-24 21:44:36', 3, '收货员L', NULL, 0, '2024-08-21 21:44:36', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (65, 101, '天地华宇', 'YT71839136', '2024-01-06 23:42:33', '2024-01-11 23:42:33', NULL, 2, '收货员O', NULL, 0, '2024-01-06 23:42:33', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (66, 102, '申通快递', 'YT39332998', '2024-01-09 08:59:02', '2024-01-12 08:59:02', NULL, 2, '收货员T', NULL, 0, '2024-01-09 08:59:02', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (67, 103, '顺丰速运', 'SF18718567', '2025-08-30 01:38:59', '2025-09-03 01:38:59', '2025-09-04 01:38:59', 3, '收货员R', NULL, 0, '2025-08-30 01:38:59', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (68, 104, '中通快递', 'YT32005996', '2024-02-23 07:13:52', '2024-02-26 07:13:52', NULL, 2, '收货员T', NULL, 0, '2024-02-23 07:13:52', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (69, 105, '顺丰速运', 'YT32372399', '2024-09-04 14:03:08', '2024-09-07 14:03:08', NULL, 2, '收货员D', NULL, 0, '2024-09-04 14:03:08', '2026-05-06 19:42:11');
INSERT INTO `logistics` VALUES (70, 107, '申通快递', 'YT18725623', '2025-03-27 05:14:17', '2025-04-01 05:14:17', '2025-03-31 05:14:17', 3, '收货员F', NULL, 0, '2025-03-27 05:14:17', '2026-05-06 19:42:12');
INSERT INTO `logistics` VALUES (71, 108, '德邦物流', 'YT67825657', '2024-06-28 04:12:09', '2024-07-02 04:12:09', NULL, 2, '收货员J', NULL, 0, '2024-06-28 04:12:09', '2026-05-06 19:42:12');
INSERT INTO `logistics` VALUES (72, 112, '佳吉快运', 'YT70001492', '2024-12-09 18:14:35', '2024-12-15 18:14:35', NULL, 2, '收货员O', NULL, 0, '2024-12-09 18:14:35', '2026-05-06 19:42:12');
INSERT INTO `logistics` VALUES (73, 113, '圆通速递', 'SF60472296', '2024-10-14 22:29:00', '2024-10-17 22:29:00', '2024-10-17 22:29:00', 3, '收货员B', NULL, 0, '2024-10-14 22:29:00', '2026-05-06 19:42:12');
INSERT INTO `logistics` VALUES (74, 114, '圆通速递', 'SF11534572', '2025-08-06 05:35:54', '2025-08-11 05:35:54', NULL, 2, '收货员W', NULL, 0, '2025-08-06 05:35:54', '2026-05-06 19:42:12');
INSERT INTO `logistics` VALUES (75, 115, '安能物流', 'YT49615210', '2024-10-20 22:02:18', '2024-10-25 22:02:18', '2024-10-24 22:02:18', 3, '收货员H', NULL, 0, '2024-10-20 22:02:18', '2026-05-06 19:42:12');
INSERT INTO `logistics` VALUES (76, 116, '顺丰速运', 'YT25593614', '2025-12-17 02:42:58', '2025-12-24 02:42:58', '2025-12-25 02:42:58', 3, '收货员T', NULL, 0, '2025-12-17 02:42:58', '2026-05-06 19:42:12');
INSERT INTO `logistics` VALUES (77, 117, '德邦物流', 'YT5300729', '2024-03-11 13:24:11', '2024-03-18 13:24:11', NULL, 2, '收货员E', NULL, 0, '2024-03-11 13:24:11', '2026-05-06 19:42:12');
INSERT INTO `logistics` VALUES (78, 120, '圆通速递', 'SF16724209', '2025-12-18 06:00:45', '2025-12-22 06:00:45', NULL, 2, '收货员U', NULL, 0, '2025-12-18 06:00:45', '2026-05-06 19:42:12');

-- ----------------------------
-- Table structure for order_detail
-- ----------------------------
DROP TABLE IF EXISTS `order_detail`;
CREATE TABLE `order_detail`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT '明细ID',
  `order_id` bigint(0) NOT NULL COMMENT '订单ID',
  `part_id` bigint(0) NOT NULL COMMENT '零部件ID',
  `quantity` int(0) NOT NULL DEFAULT 1 COMMENT '采购数量',
  `unit_price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '采购单价',
  `subtotal` decimal(12, 2) GENERATED ALWAYS AS ((`quantity` * `unit_price`)) STORED COMMENT '小计金额' NULL,
  `remark` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '备注',
  `deleted` tinyint(0) NULL DEFAULT 0 COMMENT '删除标志',
  `create_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `update_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_order_id`(`order_id`) USING BTREE,
  INDEX `idx_part_id`(`part_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 635 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '订单明细表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of order_detail
-- ----------------------------
INSERT INTO `order_detail` VALUES (1, 1, 29, 7, 215.00, DEFAULT, NULL, 0, '2025-12-25 22:18:37', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (2, 1, 17, 6, 496.00, DEFAULT, NULL, 0, '2025-12-25 22:18:37', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (3, 2, 30, 24, 88.00, DEFAULT, NULL, 0, '2025-04-01 07:59:21', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (4, 2, 49, 15, 1209.00, DEFAULT, NULL, 0, '2025-04-01 07:59:21', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (5, 2, 34, 18, 446.00, DEFAULT, NULL, 0, '2025-04-01 07:59:21', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (6, 2, 3, 12, 4744.00, DEFAULT, NULL, 0, '2025-04-01 07:59:21', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (7, 2, 52, 19, 1816.00, DEFAULT, NULL, 0, '2025-04-01 07:59:21', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (8, 2, 43, 22, 33.00, DEFAULT, NULL, 0, '2025-04-01 07:59:21', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (9, 3, 52, 8, 1816.00, DEFAULT, NULL, 0, '2025-05-22 18:18:50', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (10, 3, 24, 9, 207.00, DEFAULT, NULL, 0, '2025-05-22 18:18:50', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (11, 3, 11, 18, 4372.00, DEFAULT, NULL, 0, '2025-05-22 18:18:50', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (12, 3, 58, 11, 181.00, DEFAULT, NULL, 0, '2025-05-22 18:18:50', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (13, 3, 48, 8, 4781.00, DEFAULT, NULL, 0, '2025-05-22 18:18:50', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (14, 4, 61, 19, 147.00, DEFAULT, NULL, 0, '2024-10-19 12:12:30', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (15, 4, 54, 22, 1619.00, DEFAULT, NULL, 0, '2024-10-19 12:12:30', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (16, 4, 59, 8, 476.00, DEFAULT, NULL, 0, '2024-10-19 12:12:30', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (17, 4, 30, 24, 88.00, DEFAULT, NULL, 0, '2024-10-19 12:12:30', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (18, 5, 19, 17, 445.00, DEFAULT, NULL, 0, '2024-11-02 02:31:52', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (19, 5, 30, 6, 88.00, DEFAULT, NULL, 0, '2024-11-02 02:31:52', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (20, 5, 36, 21, 249.00, DEFAULT, NULL, 0, '2024-11-02 02:31:52', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (21, 5, 39, 9, 359.00, DEFAULT, NULL, 0, '2024-11-02 02:31:52', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (22, 5, 24, 5, 207.00, DEFAULT, NULL, 0, '2024-11-02 02:31:52', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (23, 5, 35, 12, 59.00, DEFAULT, NULL, 0, '2024-11-02 02:31:52', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (24, 6, 45, 21, 2482.00, DEFAULT, NULL, 0, '2025-09-09 17:51:17', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (25, 6, 32, 9, 495.00, DEFAULT, NULL, 0, '2025-09-09 17:51:17', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (26, 6, 25, 11, 78.00, DEFAULT, NULL, 0, '2025-09-09 17:51:17', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (27, 7, 36, 16, 249.00, DEFAULT, NULL, 0, '2025-03-06 11:24:41', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (28, 7, 57, 21, 242.00, DEFAULT, NULL, 0, '2025-03-06 11:24:41', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (29, 7, 39, 20, 359.00, DEFAULT, NULL, 0, '2025-03-06 11:24:41', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (30, 7, 21, 6, 247.00, DEFAULT, NULL, 0, '2025-03-06 11:24:41', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (31, 7, 14, 16, 281.00, DEFAULT, NULL, 0, '2025-03-06 11:24:41', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (32, 7, 49, 5, 1209.00, DEFAULT, NULL, 0, '2025-03-06 11:24:41', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (33, 7, 8, 20, 2399.00, DEFAULT, NULL, 0, '2025-03-06 11:24:41', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (34, 8, 59, 10, 476.00, DEFAULT, NULL, 0, '2024-02-04 19:08:47', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (35, 8, 50, 20, 1981.00, DEFAULT, NULL, 0, '2024-02-04 19:08:47', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (36, 8, 37, 15, 110.00, DEFAULT, NULL, 0, '2024-02-04 19:08:47', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (37, 9, 18, 18, 232.00, DEFAULT, NULL, 0, '2025-06-19 19:10:09', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (38, 9, 57, 11, 242.00, DEFAULT, NULL, 0, '2025-06-19 19:10:09', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (39, 10, 63, 23, 146.00, DEFAULT, NULL, 0, '2024-08-18 00:58:49', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (40, 10, 46, 6, 2557.00, DEFAULT, NULL, 0, '2024-08-18 00:58:49', '2026-05-06 19:41:54');
INSERT INTO `order_detail` VALUES (41, 10, 57, 23, 242.00, DEFAULT, NULL, 0, '2024-08-18 00:58:49', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (42, 10, 21, 20, 247.00, DEFAULT, NULL, 0, '2024-08-18 00:58:49', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (43, 11, 43, 10, 33.00, DEFAULT, NULL, 0, '2025-08-20 00:36:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (44, 11, 7, 10, 4589.00, DEFAULT, NULL, 0, '2025-08-20 00:36:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (45, 11, 49, 5, 1209.00, DEFAULT, NULL, 0, '2025-08-20 00:36:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (46, 11, 41, 15, 359.00, DEFAULT, NULL, 0, '2025-08-20 00:36:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (47, 11, 26, 10, 251.00, DEFAULT, NULL, 0, '2025-08-20 00:36:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (48, 11, 23, 5, 180.00, DEFAULT, NULL, 0, '2025-08-20 00:36:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (49, 12, 54, 8, 1619.00, DEFAULT, NULL, 0, '2025-08-28 18:27:23', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (50, 12, 56, 12, 58.00, DEFAULT, NULL, 0, '2025-08-28 18:27:23', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (51, 12, 11, 14, 4372.00, DEFAULT, NULL, 0, '2025-08-28 18:27:23', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (52, 12, 16, 7, 117.00, DEFAULT, NULL, 0, '2025-08-28 18:27:23', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (53, 12, 24, 20, 207.00, DEFAULT, NULL, 0, '2025-08-28 18:27:23', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (54, 12, 52, 8, 1816.00, DEFAULT, NULL, 0, '2025-08-28 18:27:23', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (55, 13, 59, 13, 476.00, DEFAULT, NULL, 0, '2024-10-23 05:38:54', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (56, 13, 40, 14, 447.00, DEFAULT, NULL, 0, '2024-10-23 05:38:54', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (57, 13, 17, 8, 496.00, DEFAULT, NULL, 0, '2024-10-23 05:38:54', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (58, 13, 45, 19, 2482.00, DEFAULT, NULL, 0, '2024-10-23 05:38:54', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (59, 14, 47, 11, 1616.00, DEFAULT, NULL, 0, '2025-08-26 17:13:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (60, 14, 39, 16, 359.00, DEFAULT, NULL, 0, '2025-08-26 17:13:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (61, 14, 29, 16, 215.00, DEFAULT, NULL, 0, '2025-08-26 17:13:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (62, 14, 27, 24, 301.00, DEFAULT, NULL, 0, '2025-08-26 17:13:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (63, 14, 19, 18, 445.00, DEFAULT, NULL, 0, '2025-08-26 17:13:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (64, 14, 61, 11, 147.00, DEFAULT, NULL, 0, '2025-08-26 17:13:34', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (65, 15, 52, 6, 1816.00, DEFAULT, NULL, 0, '2025-08-23 18:23:24', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (66, 15, 54, 15, 1619.00, DEFAULT, NULL, 0, '2025-08-23 18:23:24', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (67, 15, 3, 20, 4744.00, DEFAULT, NULL, 0, '2025-08-23 18:23:24', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (68, 15, 31, 9, 338.00, DEFAULT, NULL, 0, '2025-08-23 18:23:24', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (69, 15, 28, 14, 242.00, DEFAULT, NULL, 0, '2025-08-23 18:23:24', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (70, 15, 11, 5, 4372.00, DEFAULT, NULL, 0, '2025-08-23 18:23:24', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (71, 16, 57, 23, 242.00, DEFAULT, NULL, 0, '2024-01-24 02:51:20', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (72, 16, 15, 24, 366.00, DEFAULT, NULL, 0, '2024-01-24 02:51:20', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (73, 17, 2, 11, 1717.00, DEFAULT, NULL, 0, '2025-12-09 10:11:41', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (74, 17, 41, 12, 359.00, DEFAULT, NULL, 0, '2025-12-09 10:11:41', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (75, 18, 40, 17, 447.00, DEFAULT, NULL, 0, '2024-01-10 05:46:31', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (76, 18, 63, 23, 146.00, DEFAULT, NULL, 0, '2024-01-10 05:46:31', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (77, 19, 3, 20, 4744.00, DEFAULT, NULL, 0, '2025-07-12 04:15:48', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (78, 19, 61, 22, 147.00, DEFAULT, NULL, 0, '2025-07-12 04:15:48', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (79, 19, 49, 16, 1209.00, DEFAULT, NULL, 0, '2025-07-12 04:15:48', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (80, 19, 11, 23, 4372.00, DEFAULT, NULL, 0, '2025-07-12 04:15:48', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (81, 19, 19, 19, 445.00, DEFAULT, NULL, 0, '2025-07-12 04:15:48', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (82, 19, 7, 23, 4589.00, DEFAULT, NULL, 0, '2025-07-12 04:15:48', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (83, 19, 8, 10, 2399.00, DEFAULT, NULL, 0, '2025-07-12 04:15:48', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (84, 20, 28, 24, 242.00, DEFAULT, NULL, 0, '2024-11-15 01:49:01', '2026-05-06 19:41:55');
INSERT INTO `order_detail` VALUES (85, 20, 52, 7, 1816.00, DEFAULT, NULL, 0, '2024-11-15 01:49:01', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (86, 20, 21, 21, 247.00, DEFAULT, NULL, 0, '2024-11-15 01:49:01', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (87, 20, 12, 12, 2064.00, DEFAULT, NULL, 0, '2024-11-15 01:49:01', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (88, 20, 40, 13, 447.00, DEFAULT, NULL, 0, '2024-11-15 01:49:01', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (89, 20, 2, 22, 1717.00, DEFAULT, NULL, 0, '2024-11-15 01:49:01', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (90, 21, 38, 20, 462.00, DEFAULT, NULL, 0, '2025-10-08 07:54:48', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (91, 21, 35, 13, 59.00, DEFAULT, NULL, 0, '2025-10-08 07:54:48', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (92, 22, 45, 17, 2482.00, DEFAULT, NULL, 0, '2024-01-14 15:37:06', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (93, 22, 26, 12, 251.00, DEFAULT, NULL, 0, '2024-01-14 15:37:06', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (94, 23, 33, 24, 222.00, DEFAULT, NULL, 0, '2024-08-28 15:41:32', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (95, 23, 62, 23, 217.00, DEFAULT, NULL, 0, '2024-08-28 15:41:32', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (96, 23, 2, 23, 1717.00, DEFAULT, NULL, 0, '2024-08-28 15:41:32', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (97, 23, 63, 23, 146.00, DEFAULT, NULL, 0, '2024-08-28 15:41:32', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (98, 23, 14, 24, 281.00, DEFAULT, NULL, 0, '2024-08-28 15:41:32', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (99, 24, 51, 14, 1894.00, DEFAULT, NULL, 0, '2024-05-15 13:55:09', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (100, 24, 62, 11, 217.00, DEFAULT, NULL, 0, '2024-05-15 13:55:09', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (101, 24, 20, 11, 405.00, DEFAULT, NULL, 0, '2024-05-15 13:55:09', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (102, 24, 38, 24, 462.00, DEFAULT, NULL, 0, '2024-05-15 13:55:09', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (103, 24, 14, 12, 281.00, DEFAULT, NULL, 0, '2024-05-15 13:55:09', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (104, 24, 32, 24, 495.00, DEFAULT, NULL, 0, '2024-05-15 13:55:09', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (105, 24, 25, 14, 78.00, DEFAULT, NULL, 0, '2024-05-15 13:55:09', '2026-05-06 19:41:56');
INSERT INTO `order_detail` VALUES (106, 25, 4, 11, 650.00, DEFAULT, NULL, 0, '2024-11-21 10:48:18', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (107, 25, 5, 8, 4616.00, DEFAULT, NULL, 0, '2024-11-21 10:48:18', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (108, 25, 54, 9, 1619.00, DEFAULT, NULL, 0, '2024-11-21 10:48:18', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (109, 25, 20, 20, 405.00, DEFAULT, NULL, 0, '2024-11-21 10:48:18', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (110, 25, 46, 8, 2557.00, DEFAULT, NULL, 0, '2024-11-21 10:48:18', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (111, 25, 53, 23, 1991.00, DEFAULT, NULL, 0, '2024-11-21 10:48:18', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (112, 26, 20, 13, 405.00, DEFAULT, NULL, 0, '2025-12-28 17:43:44', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (113, 26, 50, 15, 1981.00, DEFAULT, NULL, 0, '2025-12-28 17:43:44', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (114, 26, 40, 5, 447.00, DEFAULT, NULL, 0, '2025-12-28 17:43:44', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (115, 26, 60, 6, 14.00, DEFAULT, NULL, 0, '2025-12-28 17:43:44', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (116, 27, 63, 12, 146.00, DEFAULT, NULL, 0, '2024-12-09 02:22:26', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (117, 27, 45, 8, 2482.00, DEFAULT, NULL, 0, '2024-12-09 02:22:26', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (118, 27, 27, 19, 301.00, DEFAULT, NULL, 0, '2024-12-09 02:22:26', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (119, 27, 38, 17, 462.00, DEFAULT, NULL, 0, '2024-12-09 02:22:26', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (120, 27, 49, 18, 1209.00, DEFAULT, NULL, 0, '2024-12-09 02:22:26', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (121, 27, 6, 19, 3759.00, DEFAULT, NULL, 0, '2024-12-09 02:22:26', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (122, 28, 49, 10, 1209.00, DEFAULT, NULL, 0, '2024-07-04 14:51:13', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (123, 28, 44, 5, 308.00, DEFAULT, NULL, 0, '2024-07-04 14:51:13', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (124, 28, 22, 10, 168.00, DEFAULT, NULL, 0, '2024-07-04 14:51:13', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (125, 28, 57, 6, 242.00, DEFAULT, NULL, 0, '2024-07-04 14:51:13', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (126, 28, 26, 18, 251.00, DEFAULT, NULL, 0, '2024-07-04 14:51:13', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (127, 29, 13, 21, 447.00, DEFAULT, NULL, 0, '2024-02-18 07:52:54', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (128, 29, 41, 5, 359.00, DEFAULT, NULL, 0, '2024-02-18 07:52:54', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (129, 29, 25, 19, 78.00, DEFAULT, NULL, 0, '2024-02-18 07:52:54', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (130, 29, 9, 13, 3454.00, DEFAULT, NULL, 0, '2024-02-18 07:52:54', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (131, 29, 57, 9, 242.00, DEFAULT, NULL, 0, '2024-02-18 07:52:54', '2026-05-06 19:41:57');
INSERT INTO `order_detail` VALUES (132, 30, 35, 8, 59.00, DEFAULT, NULL, 0, '2024-11-12 04:56:29', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (133, 30, 55, 16, 188.00, DEFAULT, NULL, 0, '2024-11-12 04:56:29', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (134, 30, 60, 23, 14.00, DEFAULT, NULL, 0, '2024-11-12 04:56:29', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (135, 30, 17, 11, 496.00, DEFAULT, NULL, 0, '2024-11-12 04:56:29', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (136, 30, 47, 15, 1616.00, DEFAULT, NULL, 0, '2024-11-12 04:56:29', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (137, 30, 54, 18, 1619.00, DEFAULT, NULL, 0, '2024-11-12 04:56:29', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (138, 31, 61, 7, 147.00, DEFAULT, NULL, 0, '2024-07-02 04:06:58', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (139, 31, 53, 18, 1991.00, DEFAULT, NULL, 0, '2024-07-02 04:06:58', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (140, 32, 5, 8, 4616.00, DEFAULT, NULL, 0, '2025-11-09 07:21:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (141, 32, 17, 8, 496.00, DEFAULT, NULL, 0, '2025-11-09 07:21:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (142, 32, 15, 24, 366.00, DEFAULT, NULL, 0, '2025-11-09 07:21:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (143, 32, 46, 18, 2557.00, DEFAULT, NULL, 0, '2025-11-09 07:21:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (144, 32, 56, 11, 58.00, DEFAULT, NULL, 0, '2025-11-09 07:21:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (145, 32, 49, 12, 1209.00, DEFAULT, NULL, 0, '2025-11-09 07:21:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (146, 33, 51, 22, 1894.00, DEFAULT, NULL, 0, '2025-01-13 11:53:19', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (147, 33, 44, 21, 308.00, DEFAULT, NULL, 0, '2025-01-13 11:53:19', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (148, 34, 58, 19, 181.00, DEFAULT, NULL, 0, '2024-02-10 02:31:26', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (149, 34, 51, 19, 1894.00, DEFAULT, NULL, 0, '2024-02-10 02:31:26', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (150, 34, 50, 16, 1981.00, DEFAULT, NULL, 0, '2024-02-10 02:31:26', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (151, 35, 51, 24, 1894.00, DEFAULT, NULL, 0, '2025-01-20 17:07:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (152, 35, 13, 5, 447.00, DEFAULT, NULL, 0, '2025-01-20 17:07:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (153, 35, 54, 12, 1619.00, DEFAULT, NULL, 0, '2025-01-20 17:07:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (154, 35, 37, 9, 110.00, DEFAULT, NULL, 0, '2025-01-20 17:07:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (155, 35, 5, 16, 4616.00, DEFAULT, NULL, 0, '2025-01-20 17:07:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (156, 35, 17, 8, 496.00, DEFAULT, NULL, 0, '2025-01-20 17:07:39', '2026-05-06 19:41:58');
INSERT INTO `order_detail` VALUES (157, 35, 16, 14, 117.00, DEFAULT, NULL, 0, '2025-01-20 17:07:39', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (158, 36, 10, 10, 2877.00, DEFAULT, NULL, 0, '2024-03-13 05:21:43', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (159, 36, 16, 10, 117.00, DEFAULT, NULL, 0, '2024-03-13 05:21:43', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (160, 36, 50, 22, 1981.00, DEFAULT, NULL, 0, '2024-03-13 05:21:43', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (161, 37, 14, 17, 281.00, DEFAULT, NULL, 0, '2025-03-21 02:21:07', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (162, 37, 43, 6, 33.00, DEFAULT, NULL, 0, '2025-03-21 02:21:07', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (163, 37, 56, 7, 58.00, DEFAULT, NULL, 0, '2025-03-21 02:21:07', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (164, 37, 19, 20, 445.00, DEFAULT, NULL, 0, '2025-03-21 02:21:07', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (165, 37, 9, 12, 3454.00, DEFAULT, NULL, 0, '2025-03-21 02:21:07', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (166, 38, 27, 12, 301.00, DEFAULT, NULL, 0, '2024-03-08 02:23:00', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (167, 38, 62, 11, 217.00, DEFAULT, NULL, 0, '2024-03-08 02:23:00', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (168, 38, 46, 21, 2557.00, DEFAULT, NULL, 0, '2024-03-08 02:23:00', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (169, 38, 55, 22, 188.00, DEFAULT, NULL, 0, '2024-03-08 02:23:00', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (170, 38, 21, 18, 247.00, DEFAULT, NULL, 0, '2024-03-08 02:23:00', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (171, 38, 42, 19, 72.00, DEFAULT, NULL, 0, '2024-03-08 02:23:00', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (172, 38, 49, 17, 1209.00, DEFAULT, NULL, 0, '2024-03-08 02:23:00', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (173, 39, 12, 10, 2064.00, DEFAULT, NULL, 0, '2025-12-26 19:23:28', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (174, 39, 59, 14, 476.00, DEFAULT, NULL, 0, '2025-12-26 19:23:28', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (175, 39, 27, 11, 301.00, DEFAULT, NULL, 0, '2025-12-26 19:23:28', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (176, 39, 29, 23, 215.00, DEFAULT, NULL, 0, '2025-12-26 19:23:28', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (177, 40, 30, 21, 88.00, DEFAULT, NULL, 0, '2025-01-25 22:07:28', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (178, 40, 46, 6, 2557.00, DEFAULT, NULL, 0, '2025-01-25 22:07:28', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (179, 40, 1, 12, 3905.00, DEFAULT, NULL, 0, '2025-01-25 22:07:28', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (180, 41, 9, 24, 3454.00, DEFAULT, NULL, 0, '2025-12-17 16:54:25', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (181, 41, 45, 6, 2482.00, DEFAULT, NULL, 0, '2025-12-17 16:54:25', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (182, 42, 32, 5, 495.00, DEFAULT, NULL, 0, '2024-12-21 02:56:26', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (183, 42, 33, 8, 222.00, DEFAULT, NULL, 0, '2024-12-21 02:56:26', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (184, 42, 22, 13, 168.00, DEFAULT, NULL, 0, '2024-12-21 02:56:26', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (185, 42, 38, 21, 462.00, DEFAULT, NULL, 0, '2024-12-21 02:56:26', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (186, 43, 44, 21, 308.00, DEFAULT, NULL, 0, '2025-07-17 08:16:49', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (187, 43, 24, 14, 207.00, DEFAULT, NULL, 0, '2025-07-17 08:16:49', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (188, 43, 7, 22, 4589.00, DEFAULT, NULL, 0, '2025-07-17 08:16:49', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (189, 43, 40, 22, 447.00, DEFAULT, NULL, 0, '2025-07-17 08:16:49', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (190, 44, 16, 8, 117.00, DEFAULT, NULL, 0, '2025-01-01 07:59:42', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (191, 44, 11, 20, 4372.00, DEFAULT, NULL, 0, '2025-01-01 07:59:42', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (192, 45, 21, 5, 247.00, DEFAULT, NULL, 0, '2025-01-11 09:10:11', '2026-05-06 19:41:59');
INSERT INTO `order_detail` VALUES (193, 45, 32, 16, 495.00, DEFAULT, NULL, 0, '2025-01-11 09:10:11', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (194, 45, 25, 13, 78.00, DEFAULT, NULL, 0, '2025-01-11 09:10:11', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (195, 45, 43, 17, 33.00, DEFAULT, NULL, 0, '2025-01-11 09:10:11', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (196, 45, 39, 21, 359.00, DEFAULT, NULL, 0, '2025-01-11 09:10:11', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (197, 46, 28, 24, 242.00, DEFAULT, NULL, 0, '2025-09-18 16:15:03', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (198, 46, 39, 6, 359.00, DEFAULT, NULL, 0, '2025-09-18 16:15:03', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (199, 47, 40, 12, 447.00, DEFAULT, NULL, 0, '2025-02-24 06:11:48', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (200, 47, 36, 12, 249.00, DEFAULT, NULL, 0, '2025-02-24 06:11:48', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (201, 48, 6, 20, 3759.00, DEFAULT, NULL, 0, '2024-11-03 04:31:14', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (202, 48, 63, 7, 146.00, DEFAULT, NULL, 0, '2024-11-03 04:31:14', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (203, 48, 26, 8, 251.00, DEFAULT, NULL, 0, '2024-11-03 04:31:14', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (204, 48, 37, 13, 110.00, DEFAULT, NULL, 0, '2024-11-03 04:31:14', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (205, 48, 25, 14, 78.00, DEFAULT, NULL, 0, '2024-11-03 04:31:14', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (206, 48, 36, 10, 249.00, DEFAULT, NULL, 0, '2024-11-03 04:31:14', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (207, 48, 30, 15, 88.00, DEFAULT, NULL, 0, '2024-11-03 04:31:14', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (208, 49, 5, 13, 4616.00, DEFAULT, NULL, 0, '2024-08-02 09:59:49', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (209, 49, 17, 18, 496.00, DEFAULT, NULL, 0, '2024-08-02 09:59:49', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (210, 50, 61, 24, 147.00, DEFAULT, NULL, 0, '2025-05-07 08:45:56', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (211, 50, 41, 11, 359.00, DEFAULT, NULL, 0, '2025-05-07 08:45:56', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (212, 50, 14, 11, 281.00, DEFAULT, NULL, 0, '2025-05-07 08:45:56', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (213, 51, 32, 6, 495.00, DEFAULT, NULL, 0, '2025-08-08 07:51:55', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (214, 51, 45, 10, 2482.00, DEFAULT, NULL, 0, '2025-08-08 07:51:55', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (215, 51, 1, 24, 3905.00, DEFAULT, NULL, 0, '2025-08-08 07:51:55', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (216, 51, 47, 21, 1616.00, DEFAULT, NULL, 0, '2025-08-08 07:51:55', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (217, 52, 5, 24, 4616.00, DEFAULT, NULL, 0, '2025-04-13 02:15:19', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (218, 52, 37, 8, 110.00, DEFAULT, NULL, 0, '2025-04-13 02:15:19', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (219, 52, 28, 16, 242.00, DEFAULT, NULL, 0, '2025-04-13 02:15:19', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (220, 52, 17, 14, 496.00, DEFAULT, NULL, 0, '2025-04-13 02:15:19', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (221, 52, 39, 9, 359.00, DEFAULT, NULL, 0, '2025-04-13 02:15:19', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (222, 52, 1, 10, 3905.00, DEFAULT, NULL, 0, '2025-04-13 02:15:19', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (223, 53, 4, 5, 650.00, DEFAULT, NULL, 0, '2025-06-26 05:46:54', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (224, 53, 46, 16, 2557.00, DEFAULT, NULL, 0, '2025-06-26 05:46:54', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (225, 54, 16, 20, 117.00, DEFAULT, NULL, 0, '2025-04-04 09:08:44', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (226, 54, 57, 22, 242.00, DEFAULT, NULL, 0, '2025-04-04 09:08:44', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (227, 54, 20, 10, 405.00, DEFAULT, NULL, 0, '2025-04-04 09:08:44', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (228, 54, 23, 18, 180.00, DEFAULT, NULL, 0, '2025-04-04 09:08:44', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (229, 54, 36, 7, 249.00, DEFAULT, NULL, 0, '2025-04-04 09:08:44', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (230, 54, 8, 11, 2399.00, DEFAULT, NULL, 0, '2025-04-04 09:08:44', '2026-05-06 19:42:00');
INSERT INTO `order_detail` VALUES (231, 54, 52, 14, 1816.00, DEFAULT, NULL, 0, '2025-04-04 09:08:44', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (232, 55, 1, 9, 3905.00, DEFAULT, NULL, 0, '2024-04-19 02:47:52', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (233, 55, 61, 21, 147.00, DEFAULT, NULL, 0, '2024-04-19 02:47:52', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (234, 55, 21, 16, 247.00, DEFAULT, NULL, 0, '2024-04-19 02:47:52', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (235, 55, 49, 20, 1209.00, DEFAULT, NULL, 0, '2024-04-19 02:47:52', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (236, 55, 24, 23, 207.00, DEFAULT, NULL, 0, '2024-04-19 02:47:52', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (237, 55, 16, 5, 117.00, DEFAULT, NULL, 0, '2024-04-19 02:47:52', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (238, 56, 39, 9, 359.00, DEFAULT, NULL, 0, '2024-12-26 16:04:39', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (239, 56, 26, 23, 251.00, DEFAULT, NULL, 0, '2024-12-26 16:04:39', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (240, 57, 61, 23, 147.00, DEFAULT, NULL, 0, '2025-05-13 05:55:26', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (241, 57, 44, 18, 308.00, DEFAULT, NULL, 0, '2025-05-13 05:55:26', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (242, 58, 10, 23, 2877.00, DEFAULT, NULL, 0, '2025-05-14 18:35:35', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (243, 58, 50, 17, 1981.00, DEFAULT, NULL, 0, '2025-05-14 18:35:35', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (244, 58, 6, 17, 3759.00, DEFAULT, NULL, 0, '2025-05-14 18:35:35', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (245, 58, 35, 10, 59.00, DEFAULT, NULL, 0, '2025-05-14 18:35:35', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (246, 58, 53, 6, 1991.00, DEFAULT, NULL, 0, '2025-05-14 18:35:35', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (247, 59, 52, 12, 1816.00, DEFAULT, NULL, 0, '2024-08-20 19:32:40', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (248, 59, 24, 20, 207.00, DEFAULT, NULL, 0, '2024-08-20 19:32:40', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (249, 59, 8, 5, 2399.00, DEFAULT, NULL, 0, '2024-08-20 19:32:40', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (250, 59, 44, 24, 308.00, DEFAULT, NULL, 0, '2024-08-20 19:32:40', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (251, 59, 34, 5, 446.00, DEFAULT, NULL, 0, '2024-08-20 19:32:40', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (252, 60, 21, 20, 247.00, DEFAULT, NULL, 0, '2024-06-17 10:38:35', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (253, 60, 37, 16, 110.00, DEFAULT, NULL, 0, '2024-06-17 10:38:35', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (254, 61, 60, 13, 14.00, DEFAULT, NULL, 0, '2024-07-24 11:17:38', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (255, 61, 26, 22, 251.00, DEFAULT, NULL, 0, '2024-07-24 11:17:38', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (256, 62, 28, 14, 242.00, DEFAULT, NULL, 0, '2024-10-22 13:23:24', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (257, 62, 53, 18, 1991.00, DEFAULT, NULL, 0, '2024-10-22 13:23:24', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (258, 62, 35, 19, 59.00, DEFAULT, NULL, 0, '2024-10-22 13:23:24', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (259, 63, 11, 22, 4372.00, DEFAULT, NULL, 0, '2024-06-03 17:22:07', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (260, 63, 27, 5, 301.00, DEFAULT, NULL, 0, '2024-06-03 17:22:07', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (261, 63, 49, 21, 1209.00, DEFAULT, NULL, 0, '2024-06-03 17:22:07', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (262, 63, 30, 19, 88.00, DEFAULT, NULL, 0, '2024-06-03 17:22:07', '2026-05-06 19:42:01');
INSERT INTO `order_detail` VALUES (263, 64, 26, 16, 251.00, DEFAULT, NULL, 0, '2025-01-04 01:10:11', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (264, 64, 44, 7, 308.00, DEFAULT, NULL, 0, '2025-01-04 01:10:11', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (265, 64, 22, 24, 168.00, DEFAULT, NULL, 0, '2025-01-04 01:10:11', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (266, 65, 41, 21, 359.00, DEFAULT, NULL, 0, '2024-04-26 06:11:34', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (267, 65, 62, 24, 217.00, DEFAULT, NULL, 0, '2024-04-26 06:11:34', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (270, 67, 41, 17, 359.00, DEFAULT, NULL, 0, '2025-09-08 19:57:32', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (271, 67, 20, 10, 405.00, DEFAULT, NULL, 0, '2025-09-08 19:57:32', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (272, 68, 12, 21, 2064.00, DEFAULT, NULL, 0, '2025-08-25 19:09:11', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (273, 68, 1, 15, 3905.00, DEFAULT, NULL, 0, '2025-08-25 19:09:11', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (274, 68, 62, 7, 217.00, DEFAULT, NULL, 0, '2025-08-25 19:09:11', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (275, 68, 21, 12, 247.00, DEFAULT, NULL, 0, '2025-08-25 19:09:11', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (276, 68, 10, 12, 2877.00, DEFAULT, NULL, 0, '2025-08-25 19:09:11', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (277, 68, 28, 19, 242.00, DEFAULT, NULL, 0, '2025-08-25 19:09:11', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (278, 69, 28, 12, 242.00, DEFAULT, NULL, 0, '2024-06-18 06:11:16', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (279, 69, 18, 20, 232.00, DEFAULT, NULL, 0, '2024-06-18 06:11:16', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (280, 69, 13, 10, 447.00, DEFAULT, NULL, 0, '2024-06-18 06:11:16', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (281, 69, 63, 14, 146.00, DEFAULT, NULL, 0, '2024-06-18 06:11:16', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (282, 70, 21, 16, 247.00, DEFAULT, NULL, 0, '2025-12-06 05:04:53', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (283, 70, 15, 15, 366.00, DEFAULT, NULL, 0, '2025-12-06 05:04:53', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (284, 70, 36, 22, 249.00, DEFAULT, NULL, 0, '2025-12-06 05:04:53', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (285, 70, 46, 12, 2557.00, DEFAULT, NULL, 0, '2025-12-06 05:04:53', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (286, 70, 1, 7, 3905.00, DEFAULT, NULL, 0, '2025-12-06 05:04:53', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (287, 70, 61, 18, 147.00, DEFAULT, NULL, 0, '2025-12-06 05:04:53', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (288, 71, 4, 12, 650.00, DEFAULT, NULL, 0, '2024-07-24 16:08:27', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (289, 71, 6, 24, 3759.00, DEFAULT, NULL, 0, '2024-07-24 16:08:27', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (290, 71, 25, 24, 78.00, DEFAULT, NULL, 0, '2024-07-24 16:08:27', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (291, 71, 32, 24, 495.00, DEFAULT, NULL, 0, '2024-07-24 16:08:27', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (292, 71, 42, 11, 72.00, DEFAULT, NULL, 0, '2024-07-24 16:08:27', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (293, 71, 5, 18, 4616.00, DEFAULT, NULL, 0, '2024-07-24 16:08:27', '2026-05-06 19:42:02');
INSERT INTO `order_detail` VALUES (294, 72, 56, 14, 58.00, DEFAULT, NULL, 0, '2025-05-08 15:52:30', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (295, 72, 48, 7, 4781.00, DEFAULT, NULL, 0, '2025-05-08 15:52:30', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (296, 72, 39, 13, 359.00, DEFAULT, NULL, 0, '2025-05-08 15:52:30', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (297, 72, 9, 8, 3454.00, DEFAULT, NULL, 0, '2025-05-08 15:52:30', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (298, 72, 30, 5, 88.00, DEFAULT, NULL, 0, '2025-05-08 15:52:30', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (299, 72, 5, 21, 4616.00, DEFAULT, NULL, 0, '2025-05-08 15:52:30', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (300, 73, 31, 18, 338.00, DEFAULT, NULL, 0, '2024-03-06 22:33:15', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (301, 73, 62, 11, 217.00, DEFAULT, NULL, 0, '2024-03-06 22:33:15', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (302, 74, 50, 24, 1981.00, DEFAULT, NULL, 0, '2025-06-28 10:20:50', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (303, 74, 37, 14, 110.00, DEFAULT, NULL, 0, '2025-06-28 10:20:50', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (304, 74, 28, 19, 242.00, DEFAULT, NULL, 0, '2025-06-28 10:20:50', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (305, 74, 59, 22, 476.00, DEFAULT, NULL, 0, '2025-06-28 10:20:50', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (306, 75, 62, 17, 217.00, DEFAULT, NULL, 0, '2024-12-15 04:58:07', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (307, 75, 1, 16, 3905.00, DEFAULT, NULL, 0, '2024-12-15 04:58:07', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (308, 75, 15, 13, 366.00, DEFAULT, NULL, 0, '2024-12-15 04:58:07', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (309, 75, 50, 20, 1981.00, DEFAULT, NULL, 0, '2024-12-15 04:58:07', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (310, 75, 31, 22, 338.00, DEFAULT, NULL, 0, '2024-12-15 04:58:07', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (311, 76, 50, 23, 1981.00, DEFAULT, NULL, 0, '2024-06-18 06:21:28', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (312, 76, 24, 20, 207.00, DEFAULT, NULL, 0, '2024-06-18 06:21:28', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (313, 76, 41, 9, 359.00, DEFAULT, NULL, 0, '2024-06-18 06:21:28', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (314, 76, 49, 8, 1209.00, DEFAULT, NULL, 0, '2024-06-18 06:21:28', '2026-05-06 19:42:03');
INSERT INTO `order_detail` VALUES (315, 77, 26, 12, 251.00, DEFAULT, NULL, 0, '2024-01-24 02:15:07', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (316, 77, 15, 11, 366.00, DEFAULT, NULL, 0, '2024-01-24 02:15:07', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (317, 77, 58, 13, 181.00, DEFAULT, NULL, 0, '2024-01-24 02:15:07', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (318, 78, 7, 18, 4589.00, DEFAULT, NULL, 0, '2024-11-01 07:21:52', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (319, 78, 22, 11, 168.00, DEFAULT, NULL, 0, '2024-11-01 07:21:52', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (320, 78, 4, 19, 650.00, DEFAULT, NULL, 0, '2024-11-01 07:21:52', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (321, 78, 5, 15, 4616.00, DEFAULT, NULL, 0, '2024-11-01 07:21:52', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (322, 78, 40, 14, 447.00, DEFAULT, NULL, 0, '2024-11-01 07:21:52', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (323, 78, 37, 20, 110.00, DEFAULT, NULL, 0, '2024-11-01 07:21:52', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (324, 78, 2, 20, 1717.00, DEFAULT, NULL, 0, '2024-11-01 07:21:52', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (325, 79, 26, 19, 251.00, DEFAULT, NULL, 0, '2024-12-19 06:20:36', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (326, 79, 20, 13, 405.00, DEFAULT, NULL, 0, '2024-12-19 06:20:36', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (327, 79, 15, 22, 366.00, DEFAULT, NULL, 0, '2024-12-19 06:20:36', '2026-05-06 19:42:04');
INSERT INTO `order_detail` VALUES (328, 79, 41, 20, 359.00, DEFAULT, NULL, 0, '2024-12-19 06:20:36', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (329, 79, 12, 8, 2064.00, DEFAULT, NULL, 0, '2024-12-19 06:20:36', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (330, 79, 57, 18, 242.00, DEFAULT, NULL, 0, '2024-12-19 06:20:36', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (331, 79, 53, 5, 1991.00, DEFAULT, NULL, 0, '2024-12-19 06:20:36', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (332, 80, 6, 24, 3759.00, DEFAULT, NULL, 0, '2025-02-17 22:20:22', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (333, 80, 34, 23, 446.00, DEFAULT, NULL, 0, '2025-02-17 22:20:22', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (334, 80, 58, 24, 181.00, DEFAULT, NULL, 0, '2025-02-17 22:20:22', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (335, 81, 15, 17, 366.00, DEFAULT, NULL, 0, '2024-10-24 17:13:57', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (336, 81, 25, 19, 78.00, DEFAULT, NULL, 0, '2024-10-24 17:13:57', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (337, 81, 54, 10, 1619.00, DEFAULT, NULL, 0, '2024-10-24 17:13:57', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (338, 81, 49, 23, 1209.00, DEFAULT, NULL, 0, '2024-10-24 17:13:57', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (339, 82, 1, 19, 3905.00, DEFAULT, NULL, 0, '2025-09-17 17:24:15', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (340, 82, 30, 12, 88.00, DEFAULT, NULL, 0, '2025-09-17 17:24:15', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (341, 82, 18, 24, 232.00, DEFAULT, NULL, 0, '2025-09-17 17:24:15', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (342, 82, 9, 13, 3454.00, DEFAULT, NULL, 0, '2025-09-17 17:24:15', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (343, 83, 61, 23, 147.00, DEFAULT, NULL, 0, '2024-05-27 03:16:05', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (344, 83, 7, 22, 4589.00, DEFAULT, NULL, 0, '2024-05-27 03:16:05', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (345, 84, 10, 15, 2877.00, DEFAULT, NULL, 0, '2024-06-27 09:10:47', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (346, 84, 8, 7, 2399.00, DEFAULT, NULL, 0, '2024-06-27 09:10:47', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (347, 84, 60, 15, 14.00, DEFAULT, NULL, 0, '2024-06-27 09:10:47', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (348, 84, 44, 18, 308.00, DEFAULT, NULL, 0, '2024-06-27 09:10:47', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (349, 84, 12, 5, 2064.00, DEFAULT, NULL, 0, '2024-06-27 09:10:47', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (350, 85, 57, 6, 242.00, DEFAULT, NULL, 0, '2025-04-04 21:22:30', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (351, 85, 45, 24, 2482.00, DEFAULT, NULL, 0, '2025-04-04 21:22:30', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (352, 85, 27, 6, 301.00, DEFAULT, NULL, 0, '2025-04-04 21:22:30', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (353, 86, 20, 20, 405.00, DEFAULT, NULL, 0, '2025-11-11 21:33:36', '2026-05-06 19:42:05');
INSERT INTO `order_detail` VALUES (354, 86, 64, 5, 71.00, DEFAULT, NULL, 0, '2025-11-11 21:33:36', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (355, 86, 34, 14, 446.00, DEFAULT, NULL, 0, '2025-11-11 21:33:36', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (356, 86, 22, 18, 168.00, DEFAULT, NULL, 0, '2025-11-11 21:33:36', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (357, 86, 43, 5, 33.00, DEFAULT, NULL, 0, '2025-11-11 21:33:36', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (358, 87, 47, 17, 1616.00, DEFAULT, NULL, 0, '2024-04-15 00:08:37', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (359, 87, 37, 20, 110.00, DEFAULT, NULL, 0, '2024-04-15 00:08:37', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (360, 87, 56, 13, 58.00, DEFAULT, NULL, 0, '2024-04-15 00:08:37', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (361, 87, 3, 12, 4744.00, DEFAULT, NULL, 0, '2024-04-15 00:08:37', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (362, 88, 27, 7, 301.00, DEFAULT, NULL, 0, '2025-02-07 21:51:10', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (363, 88, 51, 5, 1894.00, DEFAULT, NULL, 0, '2025-02-07 21:51:10', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (364, 88, 40, 20, 447.00, DEFAULT, NULL, 0, '2025-02-07 21:51:10', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (365, 88, 49, 15, 1209.00, DEFAULT, NULL, 0, '2025-02-07 21:51:10', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (366, 88, 7, 19, 4589.00, DEFAULT, NULL, 0, '2025-02-07 21:51:10', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (367, 88, 3, 19, 4744.00, DEFAULT, NULL, 0, '2025-02-07 21:51:10', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (368, 89, 60, 6, 14.00, DEFAULT, NULL, 0, '2025-05-10 22:10:47', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (369, 89, 17, 19, 496.00, DEFAULT, NULL, 0, '2025-05-10 22:10:47', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (370, 89, 8, 18, 2399.00, DEFAULT, NULL, 0, '2025-05-10 22:10:47', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (371, 89, 1, 10, 3905.00, DEFAULT, NULL, 0, '2025-05-10 22:10:47', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (372, 89, 6, 7, 3759.00, DEFAULT, NULL, 0, '2025-05-10 22:10:47', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (373, 89, 55, 9, 188.00, DEFAULT, NULL, 0, '2025-05-10 22:10:47', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (374, 90, 17, 8, 496.00, DEFAULT, NULL, 0, '2025-09-11 17:55:27', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (375, 90, 47, 5, 1616.00, DEFAULT, NULL, 0, '2025-09-11 17:55:27', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (376, 90, 58, 22, 181.00, DEFAULT, NULL, 0, '2025-09-11 17:55:27', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (377, 90, 62, 13, 217.00, DEFAULT, NULL, 0, '2025-09-11 17:55:27', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (378, 90, 31, 18, 338.00, DEFAULT, NULL, 0, '2025-09-11 17:55:27', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (379, 90, 18, 6, 232.00, DEFAULT, NULL, 0, '2025-09-11 17:55:27', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (380, 91, 30, 18, 88.00, DEFAULT, NULL, 0, '2024-12-23 06:52:36', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (381, 91, 19, 15, 445.00, DEFAULT, NULL, 0, '2024-12-23 06:52:36', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (382, 91, 6, 9, 3759.00, DEFAULT, NULL, 0, '2024-12-23 06:52:36', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (383, 92, 43, 14, 33.00, DEFAULT, NULL, 0, '2024-04-09 08:03:53', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (384, 92, 26, 21, 251.00, DEFAULT, NULL, 0, '2024-04-09 08:03:53', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (385, 92, 44, 16, 308.00, DEFAULT, NULL, 0, '2024-04-09 08:03:53', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (386, 92, 42, 7, 72.00, DEFAULT, NULL, 0, '2024-04-09 08:03:53', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (387, 92, 37, 24, 110.00, DEFAULT, NULL, 0, '2024-04-09 08:03:53', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (388, 92, 61, 9, 147.00, DEFAULT, NULL, 0, '2024-04-09 08:03:53', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (389, 93, 46, 6, 2557.00, DEFAULT, NULL, 0, '2024-08-08 10:07:15', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (390, 93, 61, 8, 147.00, DEFAULT, NULL, 0, '2024-08-08 10:07:15', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (391, 93, 37, 21, 110.00, DEFAULT, NULL, 0, '2024-08-08 10:07:15', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (392, 93, 60, 16, 14.00, DEFAULT, NULL, 0, '2024-08-08 10:07:15', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (393, 93, 22, 19, 168.00, DEFAULT, NULL, 0, '2024-08-08 10:07:15', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (394, 94, 26, 5, 251.00, DEFAULT, NULL, 0, '2025-10-11 05:09:35', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (395, 94, 31, 10, 338.00, DEFAULT, NULL, 0, '2025-10-11 05:09:35', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (396, 94, 53, 6, 1991.00, DEFAULT, NULL, 0, '2025-10-11 05:09:35', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (397, 94, 18, 11, 232.00, DEFAULT, NULL, 0, '2025-10-11 05:09:35', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (398, 94, 20, 17, 405.00, DEFAULT, NULL, 0, '2025-10-11 05:09:35', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (399, 95, 47, 7, 1616.00, DEFAULT, NULL, 0, '2025-05-13 00:28:15', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (400, 95, 29, 14, 215.00, DEFAULT, NULL, 0, '2025-05-13 00:28:15', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (401, 95, 36, 20, 249.00, DEFAULT, NULL, 0, '2025-05-13 00:28:15', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (402, 96, 23, 15, 180.00, DEFAULT, NULL, 0, '2025-02-28 19:46:26', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (403, 96, 14, 21, 281.00, DEFAULT, NULL, 0, '2025-02-28 19:46:26', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (404, 96, 26, 22, 251.00, DEFAULT, NULL, 0, '2025-02-28 19:46:26', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (405, 96, 30, 15, 88.00, DEFAULT, NULL, 0, '2025-02-28 19:46:26', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (406, 96, 42, 15, 72.00, DEFAULT, NULL, 0, '2025-02-28 19:46:26', '2026-05-06 19:42:06');
INSERT INTO `order_detail` VALUES (407, 97, 44, 7, 308.00, DEFAULT, NULL, 0, '2024-09-06 14:46:55', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (408, 97, 7, 24, 4589.00, DEFAULT, NULL, 0, '2024-09-06 14:46:55', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (409, 97, 31, 6, 338.00, DEFAULT, NULL, 0, '2024-09-06 14:46:55', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (410, 97, 2, 15, 1717.00, DEFAULT, NULL, 0, '2024-09-06 14:46:55', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (411, 97, 19, 6, 445.00, DEFAULT, NULL, 0, '2024-09-06 14:46:55', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (412, 97, 56, 5, 58.00, DEFAULT, NULL, 0, '2024-09-06 14:46:55', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (413, 97, 58, 12, 181.00, DEFAULT, NULL, 0, '2024-09-06 14:46:55', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (414, 98, 7, 15, 4589.00, DEFAULT, NULL, 0, '2025-06-13 09:17:44', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (415, 98, 41, 21, 359.00, DEFAULT, NULL, 0, '2025-06-13 09:17:44', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (416, 98, 9, 9, 3454.00, DEFAULT, NULL, 0, '2025-06-13 09:17:44', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (417, 98, 39, 10, 359.00, DEFAULT, NULL, 0, '2025-06-13 09:17:44', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (418, 98, 27, 9, 301.00, DEFAULT, NULL, 0, '2025-06-13 09:17:44', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (419, 98, 61, 16, 147.00, DEFAULT, NULL, 0, '2025-06-13 09:17:44', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (420, 98, 28, 21, 242.00, DEFAULT, NULL, 0, '2025-06-13 09:17:44', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (421, 99, 37, 9, 110.00, DEFAULT, NULL, 0, '2025-12-03 05:00:05', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (422, 99, 56, 17, 58.00, DEFAULT, NULL, 0, '2025-12-03 05:00:05', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (423, 99, 42, 14, 72.00, DEFAULT, NULL, 0, '2025-12-03 05:00:05', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (424, 99, 40, 13, 447.00, DEFAULT, NULL, 0, '2025-12-03 05:00:05', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (425, 99, 14, 5, 281.00, DEFAULT, NULL, 0, '2025-12-03 05:00:05', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (426, 99, 26, 10, 251.00, DEFAULT, NULL, 0, '2025-12-03 05:00:05', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (427, 99, 24, 17, 207.00, DEFAULT, NULL, 0, '2025-12-03 05:00:05', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (428, 100, 40, 14, 447.00, DEFAULT, NULL, 0, '2024-08-18 21:44:36', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (429, 100, 17, 18, 496.00, DEFAULT, NULL, 0, '2024-08-18 21:44:36', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (430, 100, 45, 15, 2482.00, DEFAULT, NULL, 0, '2024-08-18 21:44:36', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (431, 101, 32, 16, 495.00, DEFAULT, NULL, 0, '2024-01-03 23:42:33', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (432, 101, 2, 24, 1717.00, DEFAULT, NULL, 0, '2024-01-03 23:42:33', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (433, 101, 42, 13, 72.00, DEFAULT, NULL, 0, '2024-01-03 23:42:33', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (434, 101, 64, 23, 71.00, DEFAULT, NULL, 0, '2024-01-03 23:42:33', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (435, 102, 22, 5, 168.00, DEFAULT, NULL, 0, '2024-01-07 08:59:02', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (436, 102, 45, 6, 2482.00, DEFAULT, NULL, 0, '2024-01-07 08:59:02', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (437, 102, 34, 13, 446.00, DEFAULT, NULL, 0, '2024-01-07 08:59:02', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (438, 102, 3, 12, 4744.00, DEFAULT, NULL, 0, '2024-01-07 08:59:02', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (439, 102, 5, 18, 4616.00, DEFAULT, NULL, 0, '2024-01-07 08:59:02', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (440, 102, 11, 23, 4372.00, DEFAULT, NULL, 0, '2024-01-07 08:59:02', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (441, 103, 16, 5, 117.00, DEFAULT, NULL, 0, '2025-08-27 01:38:59', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (442, 103, 41, 22, 359.00, DEFAULT, NULL, 0, '2025-08-27 01:38:59', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (443, 103, 43, 10, 33.00, DEFAULT, NULL, 0, '2025-08-27 01:38:59', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (444, 103, 27, 7, 301.00, DEFAULT, NULL, 0, '2025-08-27 01:38:59', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (445, 104, 17, 13, 496.00, DEFAULT, NULL, 0, '2024-02-22 07:13:52', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (446, 104, 26, 6, 251.00, DEFAULT, NULL, 0, '2024-02-22 07:13:52', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (447, 104, 45, 21, 2482.00, DEFAULT, NULL, 0, '2024-02-22 07:13:52', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (448, 104, 7, 12, 4589.00, DEFAULT, NULL, 0, '2024-02-22 07:13:52', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (449, 105, 19, 15, 445.00, DEFAULT, NULL, 0, '2024-09-02 14:03:08', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (450, 105, 55, 19, 188.00, DEFAULT, NULL, 0, '2024-09-02 14:03:08', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (451, 105, 46, 10, 2557.00, DEFAULT, NULL, 0, '2024-09-02 14:03:08', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (452, 106, 12, 19, 2064.00, DEFAULT, NULL, 0, '2024-03-12 17:38:49', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (453, 106, 53, 6, 1991.00, DEFAULT, NULL, 0, '2024-03-12 17:38:49', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (454, 106, 21, 18, 247.00, DEFAULT, NULL, 0, '2024-03-12 17:38:49', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (455, 106, 8, 7, 2399.00, DEFAULT, NULL, 0, '2024-03-12 17:38:49', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (456, 106, 9, 13, 3454.00, DEFAULT, NULL, 0, '2024-03-12 17:38:49', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (457, 106, 32, 5, 495.00, DEFAULT, NULL, 0, '2024-03-12 17:38:49', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (458, 106, 45, 7, 2482.00, DEFAULT, NULL, 0, '2024-03-12 17:38:49', '2026-05-06 19:42:07');
INSERT INTO `order_detail` VALUES (459, 107, 48, 20, 4781.00, DEFAULT, NULL, 0, '2025-03-25 05:14:17', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (460, 107, 53, 21, 1991.00, DEFAULT, NULL, 0, '2025-03-25 05:14:17', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (461, 107, 21, 6, 247.00, DEFAULT, NULL, 0, '2025-03-25 05:14:17', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (462, 107, 45, 17, 2482.00, DEFAULT, NULL, 0, '2025-03-25 05:14:17', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (463, 107, 26, 10, 251.00, DEFAULT, NULL, 0, '2025-03-25 05:14:17', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (464, 108, 49, 20, 1209.00, DEFAULT, NULL, 0, '2024-06-27 04:12:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (465, 108, 9, 22, 3454.00, DEFAULT, NULL, 0, '2024-06-27 04:12:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (466, 108, 32, 5, 495.00, DEFAULT, NULL, 0, '2024-06-27 04:12:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (467, 108, 22, 6, 168.00, DEFAULT, NULL, 0, '2024-06-27 04:12:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (468, 108, 14, 22, 281.00, DEFAULT, NULL, 0, '2024-06-27 04:12:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (469, 108, 52, 22, 1816.00, DEFAULT, NULL, 0, '2024-06-27 04:12:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (470, 109, 62, 11, 217.00, DEFAULT, NULL, 0, '2024-11-19 14:53:57', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (471, 109, 1, 22, 3905.00, DEFAULT, NULL, 0, '2024-11-19 14:53:57', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (472, 110, 14, 6, 281.00, DEFAULT, NULL, 0, '2024-05-02 09:21:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (473, 110, 46, 24, 2557.00, DEFAULT, NULL, 0, '2024-05-02 09:21:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (474, 110, 28, 8, 242.00, DEFAULT, NULL, 0, '2024-05-02 09:21:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (475, 110, 54, 12, 1619.00, DEFAULT, NULL, 0, '2024-05-02 09:21:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (476, 110, 60, 7, 14.00, DEFAULT, NULL, 0, '2024-05-02 09:21:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (477, 110, 50, 8, 1981.00, DEFAULT, NULL, 0, '2024-05-02 09:21:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (478, 110, 26, 12, 251.00, DEFAULT, NULL, 0, '2024-05-02 09:21:09', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (479, 111, 11, 17, 4372.00, DEFAULT, NULL, 0, '2025-08-17 03:16:55', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (480, 111, 26, 10, 251.00, DEFAULT, NULL, 0, '2025-08-17 03:16:55', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (481, 111, 33, 6, 222.00, DEFAULT, NULL, 0, '2025-08-17 03:16:55', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (482, 111, 47, 11, 1616.00, DEFAULT, NULL, 0, '2025-08-17 03:16:55', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (483, 111, 15, 5, 366.00, DEFAULT, NULL, 0, '2025-08-17 03:16:55', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (484, 111, 31, 7, 338.00, DEFAULT, NULL, 0, '2025-08-17 03:16:55', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (485, 112, 62, 15, 217.00, DEFAULT, NULL, 0, '2024-12-07 18:14:35', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (486, 112, 41, 5, 359.00, DEFAULT, NULL, 0, '2024-12-07 18:14:35', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (487, 112, 29, 22, 215.00, DEFAULT, NULL, 0, '2024-12-07 18:14:35', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (488, 112, 20, 24, 405.00, DEFAULT, NULL, 0, '2024-12-07 18:14:35', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (489, 112, 46, 22, 2557.00, DEFAULT, NULL, 0, '2024-12-07 18:14:35', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (490, 112, 48, 11, 4781.00, DEFAULT, NULL, 0, '2024-12-07 18:14:35', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (491, 113, 5, 10, 4616.00, DEFAULT, NULL, 0, '2024-10-13 22:29:00', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (492, 113, 63, 14, 146.00, DEFAULT, NULL, 0, '2024-10-13 22:29:00', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (493, 113, 42, 9, 72.00, DEFAULT, NULL, 0, '2024-10-13 22:29:00', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (494, 114, 55, 22, 188.00, DEFAULT, NULL, 0, '2025-08-05 05:35:54', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (495, 114, 64, 24, 71.00, DEFAULT, NULL, 0, '2025-08-05 05:35:54', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (496, 114, 28, 5, 242.00, DEFAULT, NULL, 0, '2025-08-05 05:35:54', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (497, 114, 38, 14, 462.00, DEFAULT, NULL, 0, '2025-08-05 05:35:54', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (498, 114, 57, 7, 242.00, DEFAULT, NULL, 0, '2025-08-05 05:35:54', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (499, 115, 15, 16, 366.00, DEFAULT, NULL, 0, '2024-10-17 22:02:18', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (500, 115, 12, 6, 2064.00, DEFAULT, NULL, 0, '2024-10-17 22:02:18', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (501, 116, 17, 8, 496.00, DEFAULT, NULL, 0, '2025-12-15 02:42:58', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (502, 116, 48, 11, 4781.00, DEFAULT, NULL, 0, '2025-12-15 02:42:58', '2026-05-06 19:42:08');
INSERT INTO `order_detail` VALUES (503, 116, 21, 14, 247.00, DEFAULT, NULL, 0, '2025-12-15 02:42:58', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (504, 116, 55, 13, 188.00, DEFAULT, NULL, 0, '2025-12-15 02:42:58', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (505, 117, 46, 19, 2557.00, DEFAULT, NULL, 0, '2024-03-08 13:24:11', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (506, 117, 6, 15, 3759.00, DEFAULT, NULL, 0, '2024-03-08 13:24:11', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (507, 117, 35, 5, 59.00, DEFAULT, NULL, 0, '2024-03-08 13:24:11', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (508, 117, 39, 5, 359.00, DEFAULT, NULL, 0, '2024-03-08 13:24:11', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (509, 118, 46, 17, 2557.00, DEFAULT, NULL, 0, '2025-08-06 02:55:55', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (510, 118, 22, 6, 168.00, DEFAULT, NULL, 0, '2025-08-06 02:55:55', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (511, 118, 56, 18, 58.00, DEFAULT, NULL, 0, '2025-08-06 02:55:55', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (512, 119, 6, 22, 3759.00, DEFAULT, NULL, 0, '2025-10-19 18:24:41', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (513, 119, 25, 15, 78.00, DEFAULT, NULL, 0, '2025-10-19 18:24:41', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (514, 120, 26, 24, 251.00, DEFAULT, NULL, 0, '2025-12-17 06:00:45', '2026-05-06 19:42:09');
INSERT INTO `order_detail` VALUES (515, 121, 1, 10, 158.00, DEFAULT, NULL, NULL, NULL, NULL);
INSERT INTO `order_detail` VALUES (516, 122, 15, 386, 1705.55, DEFAULT, '测试明细-1', NULL, NULL, NULL);
INSERT INTO `order_detail` VALUES (517, 122, 164, 424, 4615.08, DEFAULT, '测试明细-2', NULL, NULL, NULL);
INSERT INTO `order_detail` VALUES (519, 123, 32, 170, 2303.66, DEFAULT, '测试明细-1', NULL, NULL, NULL);
INSERT INTO `order_detail` VALUES (520, 123, 36, 23, 2922.54, DEFAULT, '测试明细-2', NULL, NULL, NULL);
INSERT INTO `order_detail` VALUES (521, 124, 66, 28, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (522, 124, 67, 27, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (523, 124, 65, 33, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (524, 125, 67, 23, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (525, 125, 65, 23, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (526, 125, 66, 25, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (527, 126, 65, 20, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (528, 127, 66, 31, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (529, 127, 65, 19, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (530, 127, 67, 13, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (531, 128, 65, 15, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (532, 128, 66, 34, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (533, 129, 67, 31, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (534, 130, 65, 21, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (535, 131, 65, 36, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (536, 132, 65, 31, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (537, 133, 66, 38, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (538, 133, 67, 20, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (539, 133, 65, 15, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (540, 134, 66, 25, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (541, 134, 67, 33, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (542, 135, 65, 15, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (543, 136, 66, 30, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (544, 136, 67, 24, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (545, 137, 65, 16, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (546, 137, 66, 18, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (547, 137, 67, 37, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (548, 138, 67, 13, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (549, 139, 65, 10, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (550, 139, 66, 36, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (551, 139, 67, 38, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (552, 140, 66, 38, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `order_detail` VALUES (553, 141, 65, 17, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (554, 142, 65, 34, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (555, 142, 66, 10, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (556, 143, 66, 37, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (557, 143, 67, 16, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (558, 143, 65, 35, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (559, 144, 66, 10, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (560, 144, 65, 39, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (561, 144, 67, 31, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (562, 145, 67, 39, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (563, 145, 65, 22, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (564, 145, 66, 27, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (565, 146, 67, 22, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (566, 146, 65, 25, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (567, 146, 66, 38, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (568, 147, 67, 37, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (569, 147, 65, 13, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (570, 148, 66, 25, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (571, 148, 65, 20, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (572, 149, 67, 18, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (573, 149, 66, 37, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (574, 150, 66, 36, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (575, 150, 65, 12, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (576, 150, 67, 35, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (577, 151, 65, 39, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (578, 152, 65, 23, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (579, 152, 67, 20, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (580, 152, 66, 18, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (581, 153, 66, 38, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (582, 154, 66, 20, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (583, 155, 65, 14, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (584, 156, 66, 25, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (585, 156, 65, 13, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (586, 157, 65, 10, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (587, 157, 66, 30, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (588, 158, 67, 36, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (589, 158, 66, 27, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (590, 159, 66, 26, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (591, 160, 65, 17, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (592, 161, 65, 22, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (593, 162, 65, 20, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (594, 162, 66, 23, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (595, 163, 66, 27, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (596, 164, 65, 23, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (597, 165, 65, 20, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (598, 165, 66, 32, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (599, 166, 66, 28, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (600, 166, 65, 10, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (601, 167, 65, 16, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (602, 167, 66, 36, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (603, 167, 67, 24, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (604, 168, 65, 25, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (605, 169, 67, 25, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (606, 169, 66, 14, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (607, 170, 65, 35, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (608, 170, 67, 27, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (609, 171, 65, 33, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (610, 171, 67, 25, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (611, 171, 66, 10, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (612, 172, 66, 21, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (613, 172, 67, 33, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (614, 173, 67, 29, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (615, 173, 65, 36, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (616, 173, 66, 35, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (617, 174, 67, 11, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (618, 175, 67, 24, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (619, 175, 65, 26, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (620, 176, 66, 15, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (621, 176, 67, 17, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (622, 177, 67, 20, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (623, 177, 66, 29, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (624, 177, 65, 20, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (625, 178, 67, 21, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (626, 178, 66, 22, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (627, 179, 65, 12, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (628, 180, 67, 28, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (629, 180, 66, 35, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (630, 181, 67, 36, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (631, 181, 65, 35, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (632, 182, 67, 10, 58.00, DEFAULT, 'NGK火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (633, 182, 65, 34, 32.00, DEFAULT, 'DENSO火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `order_detail` VALUES (634, 182, 66, 28, 40.00, DEFAULT, 'BOSCH火花塞采购', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');

-- ----------------------------
-- Table structure for part
-- ----------------------------
DROP TABLE IF EXISTS `part`;
CREATE TABLE `part`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT '零部件ID',
  `part_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '零件编码',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '零件名称',
  `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '型号',
  `specification` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '规格',
  `unit` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '个' COMMENT '单位',
  `purchase_price` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '采购单价',
  `suggested_retail_price` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '建议零售价',
  `stock_warning_value` int(0) NULL DEFAULT 10 COMMENT '库存预警值',
  `supplier_id` bigint(0) NULL DEFAULT NULL COMMENT '供应商ID',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '分类',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '零件描述',
  `deleted` tinyint(0) NULL DEFAULT 0 COMMENT '删除标志',
  `create_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `update_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_part_code`(`part_code`) USING BTREE,
  INDEX `idx_supplier_id`(`supplier_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 68 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '产品/零部件表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of part
-- ----------------------------
INSERT INTO `part` VALUES (1, 'PC2001', '活塞环组件', '标准型', '四冲程通用', '套', 3905.00, 5107.03, 25, 26, '发动机类', NULL, 0, '2024-08-01 22:16:43', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (2, 'PC2002', '发动机缸体', 'CB400', '400cc', '个', 1717.00, 2534.86, 22, 27, '发动机类', NULL, 0, '2024-06-05 02:37:41', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (3, 'PC2003', '曲轴总成', 'CG125', '125cc', '个', 4744.00, 6529.66, 15, 21, '发动机类', NULL, 0, '2024-06-26 07:54:24', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (4, 'PC2004', '凸轮轴', 'GY6-125', '125cc', '个', 650.00, 788.11, 12, 16, '发动机类', NULL, 0, '2025-06-09 20:29:53', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (5, 'PC2005', '气门导管', '通用型', '6mm', '个', 4616.00, 6855.08, 10, 5, '发动机类', NULL, 0, '2025-01-18 21:27:12', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (6, 'PC2006', '连杆总成', 'CB125T', '125T', '个', 3759.00, 5345.63, 29, 26, '发动机类', NULL, 0, '2025-02-20 02:28:40', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (7, 'PC2007', '机油泵', 'GY6-125', '125cc', '个', 4589.00, 6481.87, 29, 28, '发动机类', NULL, 0, '2025-05-24 07:27:08', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (8, 'PC2008', '水泵总成', 'CB400', '400cc', '个', 2399.00, 3383.90, 12, 3, '发动机类', NULL, 0, '2025-09-02 22:12:42', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (9, 'PC2009', '化油器总成', 'CG125', '125cc', '套', 3454.00, 4809.75, 28, 24, '发动机类', NULL, 0, '2025-10-26 08:19:19', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (10, 'PC2010', '离合器片', 'CB400', '400cc', '套', 2877.00, 3476.20, 19, 27, '发动机类', NULL, 0, '2024-08-12 03:43:03', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (11, 'PC2011', '启动电机', 'GY6-125', '125cc', '个', 4372.00, 6457.64, 28, 8, '发动机类', NULL, 0, '2024-12-16 00:12:26', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (12, 'PC2012', '发电机总成', 'CB125T', '125T', '个', 2064.00, 3046.97, 20, 6, '发动机类', NULL, 0, '2025-09-07 03:48:43', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (13, 'FC3001', '前减震器', '钻豹', 'KH100', '对', 447.00, 554.89, 11, 4, '车架类', NULL, 0, '2025-08-27 15:19:51', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (14, 'FC3002', '后减震器', '五羊款', '125通用', '个', 281.00, 344.42, 22, 8, '车架类', NULL, 0, '2024-07-02 03:14:45', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (15, 'FC3003', '方向把', '铝合金', '22mm', '个', 366.00, 462.16, 23, 3, '车架类', NULL, 0, '2025-01-09 10:05:00', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (16, 'FC3004', '方向柱', 'CG125', '125cc', '套', 117.00, 142.16, 20, 7, '车架类', NULL, 0, '2025-05-03 12:30:59', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (17, 'FC3005', '主支架', '五羊款', '125通用', '个', 496.00, 654.07, 21, 2, '车架类', NULL, 0, '2024-04-18 13:46:47', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (18, 'FC3006', '侧支架', 'CG125', '125通用', '个', 232.00, 279.20, 27, 12, '车架类', NULL, 0, '2025-04-12 02:46:13', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (19, 'FC3007', '链轮', '42齿', '428规格', '个', 445.00, 639.60, 13, 14, '车架类', NULL, 0, '2025-01-23 21:24:23', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (20, 'FC3008', '后平叉', '钻豹', 'KH100', '个', 405.00, 516.93, 26, 2, '车架类', NULL, 0, '2025-09-05 00:38:11', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (21, 'FC3009', '前叉总成', '太子款', '125通用', '对', 247.00, 335.95, 29, 13, '车架类', NULL, 0, '2025-02-04 06:18:20', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (22, 'FC3010', '车把开关', 'CG125', '通用', '套', 168.00, 216.58, 11, 23, '车架类', NULL, 0, '2025-10-12 22:48:42', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (23, 'EC4001', '磁电机总成', 'CG125', '125cc', '套', 180.00, 259.51, 26, 29, '电气类', NULL, 0, '2025-04-10 18:06:01', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (24, 'EC4002', '点火线圈', 'GY6-125', '125cc', '个', 207.00, 308.49, 17, 3, '电气类', NULL, 0, '2025-03-16 22:19:00', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (25, 'EC4003', '火花塞', 'NGK', 'C7HSA', '个', 78.00, 93.74, 15, 1, '电气类', NULL, 0, '2024-06-26 13:11:03', '2026-05-06 19:41:51');
INSERT INTO `part` VALUES (26, 'EC4004', '整流器', '12V', '5A', '个', 251.00, 376.03, 22, 18, '电气类', NULL, 0, '2025-08-03 05:09:10', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (27, 'EC4005', '大灯总成', '钻豹', '35W', '套', 301.00, 415.02, 18, 16, '电气类', NULL, 0, '2024-10-06 16:08:24', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (28, 'EC4006', '尾灯总成', '五羊款', 'LED', '套', 242.00, 362.08, 29, 27, '电气类', NULL, 0, '2025-01-21 23:45:19', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (29, 'EC4007', '转向灯', '通用', '10W', '对', 215.00, 282.11, 15, 24, '电气类', NULL, 0, '2024-05-05 02:59:56', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (30, 'EC4008', '仪表总成', 'CG125', '机械式', '套', 88.00, 126.86, 27, 20, '电气类', NULL, 0, '2025-02-16 15:06:50', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (31, 'EC4009', '喇叭', '12V', '双音', '个', 338.00, 434.65, 24, 27, '电气类', NULL, 0, '2024-11-19 18:41:58', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (32, 'EC4010', '闪光器', '12V', '3针', '个', 495.00, 614.11, 25, 2, '电气类', NULL, 0, '2024-05-12 19:26:52', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (33, 'EC4011', '手把开关', 'CG125', '左右套', '套', 222.00, 284.18, 20, 1, '电气类', NULL, 0, '2025-06-19 18:11:09', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (34, 'EC4012', '熄火开关', '通用', '12V', '个', 446.00, 635.78, 24, 10, '电气类', NULL, 0, '2025-01-04 15:27:03', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (35, 'BC5001', '前刹车片', '布雷博', 'GSX250', '对', 59.00, 76.60, 17, 22, '制动类', NULL, 0, '2025-10-23 13:14:06', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (36, 'BC5002', '后刹车片', 'BREMBO', 'CB400', '对', 249.00, 368.01, 24, 1, '制动类', NULL, 0, '2024-11-28 15:25:20', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (37, 'BC5003', '刹车蹄块', '通用', '130规格', '套', 110.00, 161.93, 17, 6, '制动类', NULL, 0, '2024-01-25 07:55:01', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (38, 'BC5004', '刹车泵', '日清', '直推式', '个', 462.00, 574.43, 24, 7, '制动类', NULL, 0, '2025-09-03 06:30:44', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (39, 'BC5005', '离合器手柄', '铝合金', '通用', '个', 359.00, 503.76, 15, 9, '制动类', NULL, 0, '2025-11-22 00:33:49', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (40, 'BC5006', '刹车手柄', '铝合金', '22mm', '个', 447.00, 633.75, 16, 8, '制动类', NULL, 0, '2024-01-04 09:30:28', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (41, 'BC5007', '刹车线', 'CG125', '通用', '根', 359.00, 433.02, 22, 26, '制动类', NULL, 0, '2024-10-14 00:07:48', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (42, 'BC5008', '离合线', 'CG125', '通用', '根', 72.00, 103.57, 26, 15, '制动类', NULL, 0, '2025-02-15 04:41:28', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (43, 'BC5009', '刹车总泵', '日信', '14mm', '个', 33.00, 39.98, 21, 5, '制动类', NULL, 0, '2024-11-09 05:39:59', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (44, 'BC5010', '刹车分泵', '日清', '14mm', '个', 308.00, 373.83, 21, 20, '制动类', NULL, 0, '2024-08-19 00:51:27', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (45, 'TC6001', '传动皮带', '盖茨', 'AV13x950', '根', 2482.00, 3325.08, 16, 30, '传动类', NULL, 0, '2025-12-26 19:47:27', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (46, 'TC6002', '普利珠', '12g', '8x14', '套', 2557.00, 3610.50, 13, 15, '传动类', NULL, 0, '2025-10-20 19:24:19', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (47, 'TC6003', '碗公', 'GY6-125', '125cc', '个', 1616.00, 2095.24, 17, 3, '传动类', NULL, 0, '2024-05-27 11:01:13', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (48, 'TC6004', '离合器', 'GY6-125', '125cc', '套', 4781.00, 5914.24, 13, 8, '传动类', NULL, 0, '2024-10-08 19:49:43', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (49, 'TC6005', '主动轮', 'GY6-125', '125cc', '个', 1209.00, 1555.59, 19, 18, '传动类', NULL, 0, '2025-08-14 13:46:45', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (50, 'TC6006', '从动轮', 'GY6-125', '125cc', '个', 1981.00, 2580.29, 18, 9, '传动类', NULL, 0, '2024-02-23 17:49:50', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (51, 'TC6007', '链条', '428', '120节', '根', 1894.00, 2294.93, 24, 17, '传动类', NULL, 0, '2024-02-01 14:02:54', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (52, 'TC6008', '链条接头', '428', '通用', '个', 1816.00, 2572.14, 22, 23, '传动类', NULL, 0, '2025-11-03 21:51:12', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (53, 'TC6009', '油门线', '通用', '1500mm', '根', 1991.00, 2875.05, 14, 26, '传动类', NULL, 0, '2025-04-15 11:19:38', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (54, 'TC6010', '油门把手', '通用', '22mm', '个', 1619.00, 2209.44, 26, 25, '传动类', NULL, 0, '2024-11-16 02:43:04', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (55, 'AC7001', '前挡泥板', '五羊款', '125通用', '个', 188.00, 246.81, 13, 11, '外观件', NULL, 0, '2025-07-01 23:28:14', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (56, 'AC7002', '后挡泥板', '钻豹', 'KH100', '个', 58.00, 73.14, 21, 7, '外观件', NULL, 0, '2024-06-11 19:28:38', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (57, 'AC7003', '导流罩', 'CB400', '400cc', '套', 242.00, 312.17, 19, 14, '外观件', NULL, 0, '2025-09-24 02:00:14', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (58, 'AC7004', '后视镜', '铝合金', '通用', '对', 181.00, 264.38, 14, 27, '外观件', NULL, 0, '2025-05-08 23:58:32', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (59, 'AC7005', '座垫', 'PU', '125通用', '个', 476.00, 710.62, 29, 26, '外观件', NULL, 0, '2024-04-12 05:36:08', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (60, 'AC7006', '油箱盖', 'CG125', '金属', '个', 14.00, 19.77, 25, 19, '外观件', NULL, 0, '2024-01-05 18:47:33', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (61, 'AC7007', '侧盖板', '五羊款', '125通用', '对', 147.00, 200.63, 25, 1, '外观件', NULL, 0, '2025-05-12 10:47:30', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (62, 'AC7008', '脚蹬', '铝合金', '防滑', '对', 217.00, 287.81, 20, 15, '外观件', NULL, 0, '2024-11-09 15:01:26', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (63, 'AC7009', '脚踏板', '塑料', '通用', '个', 146.00, 183.25, 13, 10, '外观件', NULL, 0, '2025-05-13 21:17:53', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (64, 'AC7010', '牌照灯', 'LED', '12V', '个', 71.00, 95.97, 17, 14, '外观件', NULL, 0, '2024-05-15 01:52:51', '2026-05-06 19:41:52');
INSERT INTO `part` VALUES (65, 'SPARK-DENSO-U27ETR', '电装DENSO火花塞 U27ETR', 'U27ETR', 'M10×1.0, 0.8mm间隙, 铱金材质, 热值27', '个', 32.00, 38.00, 20, 31, '电气类', '电装DENSO U27ETR摩托车火花塞，专为踏板车设计，采用U型槽技术和锥形电极，燃油经济性好，省油5-10%，冷车启动无忧。适用于本田CG125/雅马哈巧格125/铃木UY125等车型。', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `part` VALUES (66, 'SPARK-BOSCH-FR7DC', '博世BOSCH火花塞 FR7DC+', 'FR7DC+', 'M12×1.25, 0.9mm间隙, 铂金材质, 热值7', '个', 40.00, 48.00, 20, 32, '电气类', '博世BOSCH FR7DC+铂金火花塞，高性能摩托车专用，采用铂金中心电极技术，点火性能稳定，火焰传播均匀，减少积碳生成，使用寿命长。适用于本田CB400/雅马哈MT-07/宝马F750GS等中大排量车型。', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `part` VALUES (67, 'SPARK-NGK-CR9EIX', 'NGK铱金火花塞 Iridium IX CR9EIX', 'CR9EIX', 'M10×1.0, 0.9mm间隙, 铱金材质, 热值9', '个', 58.00, 68.00, 20, 33, '电气类', 'NGK CR9EIX Iridium IX火花塞，日本原装进口，0.9mm超细铱金中心电极设计，降低点火电压需求，提高点火可靠性。U型槽设计提高点火能量，省油效果明显约5-15%，使用寿命是普通火花塞的2-3倍。适用于本田CBR600RR/雅马哈YZF-R6/铃木GSX-R600等高性能摩托车。', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');

-- ----------------------------
-- Table structure for purchase_order
-- ----------------------------
DROP TABLE IF EXISTS `purchase_order`;
CREATE TABLE `purchase_order`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `order_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '订单编号',
  `total_amount` decimal(12, 2) NULL DEFAULT 0.00 COMMENT '订单总金额',
  `status` tinyint(0) NULL DEFAULT 1 COMMENT '订单状态',
  `order_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '下单时间',
  `expected_delivery_date` date NULL DEFAULT NULL COMMENT '预计交货日期',
  `actual_delivery_date` date NULL DEFAULT NULL COMMENT '实际交货日期',
  `created_by` bigint(0) NULL DEFAULT NULL COMMENT '创建人ID',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '备注',
  `deleted` tinyint(0) NULL DEFAULT 0 COMMENT '删除标志',
  `create_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `update_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_order_number`(`order_number`) USING BTREE,
  INDEX `idx_order_time`(`order_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 183 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '采购订单表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of purchase_order
-- ----------------------------
INSERT INTO `purchase_order` VALUES (1, 'PO2026000001', 4481.00, 4, '2025-12-25 22:18:37', '2026-01-02', '2025-12-30', 10, NULL, 0, '2025-12-25 22:18:37', '2026-05-06 19:41:54');
INSERT INTO `purchase_order` VALUES (2, 'PO2026000002', 120433.00, 4, '2025-04-01 07:59:21', '2025-04-09', '2025-04-09', 7, NULL, 0, '2025-04-01 07:59:21', '2026-05-06 19:41:54');
INSERT INTO `purchase_order` VALUES (3, 'PO2026000003', 135326.00, 2, '2025-05-22 18:18:50', '2025-05-30', NULL, 2, NULL, 0, '2025-05-22 18:18:50', '2026-05-06 19:41:54');
INSERT INTO `purchase_order` VALUES (4, 'PO2026000004', 44331.00, 3, '2024-10-19 12:12:30', '2024-10-27', NULL, 2, NULL, 0, '2024-10-19 12:12:30', '2026-05-06 19:41:54');
INSERT INTO `purchase_order` VALUES (5, 'PO2026000005', 18296.00, 2, '2024-11-02 02:31:52', '2024-11-18', NULL, 4, NULL, 0, '2024-11-02 02:31:52', '2026-05-06 19:41:54');
INSERT INTO `purchase_order` VALUES (6, 'PO2026000006', 57435.00, 2, '2025-09-09 17:51:17', '2025-09-23', NULL, 10, NULL, 0, '2025-09-09 17:51:17', '2026-05-06 19:41:54');
INSERT INTO `purchase_order` VALUES (7, 'PO2026000007', 76249.00, 2, '2025-03-06 11:24:41', '2025-03-15', NULL, 1, NULL, 0, '2025-03-06 11:24:41', '2026-05-06 19:41:54');
INSERT INTO `purchase_order` VALUES (8, 'PO2026000008', 46030.00, 4, '2024-02-04 19:08:47', '2024-02-12', '2024-02-10', 1, NULL, 0, '2024-02-04 19:08:47', '2026-05-06 19:41:54');
INSERT INTO `purchase_order` VALUES (9, 'PO2026000009', 6838.00, 3, '2025-06-19 19:10:09', '2025-07-06', NULL, 4, NULL, 0, '2025-06-19 19:10:09', '2026-05-06 19:41:54');
INSERT INTO `purchase_order` VALUES (10, 'PO2026000010', 29206.00, 2, '2024-08-18 00:58:49', '2024-09-05', NULL, 10, NULL, 0, '2024-08-18 00:58:49', '2026-05-06 19:41:55');
INSERT INTO `purchase_order` VALUES (11, 'PO2026000011', 61060.00, 5, '2025-08-20 00:36:34', '2025-09-08', NULL, 10, NULL, 0, '2025-08-20 00:36:34', '2026-05-06 19:41:55');
INSERT INTO `purchase_order` VALUES (12, 'PO2026000012', 94343.00, 1, '2025-08-28 18:27:23', '2025-09-13', NULL, 11, NULL, 0, '2025-08-28 18:27:23', '2026-05-06 19:41:55');
INSERT INTO `purchase_order` VALUES (13, 'PO2026000013', 63572.00, 2, '2024-10-23 05:38:54', '2024-11-03', NULL, 2, NULL, 0, '2024-10-23 05:38:54', '2026-05-06 19:41:55');
INSERT INTO `purchase_order` VALUES (14, 'PO2026000014', 43811.00, 2, '2025-08-26 17:13:34', '2025-09-12', NULL, 1, NULL, 0, '2025-08-26 17:13:34', '2026-05-06 19:41:55');
INSERT INTO `purchase_order` VALUES (15, 'PO2026000015', 158351.00, 4, '2025-08-23 18:23:24', '2025-08-31', '2025-09-03', 10, NULL, 0, '2025-08-23 18:23:24', '2026-05-06 19:41:55');
INSERT INTO `purchase_order` VALUES (16, 'PO2026000016', 14350.00, 4, '2024-01-24 02:51:20', '2024-02-03', '2024-02-06', 4, NULL, 0, '2024-01-24 02:51:20', '2026-05-06 19:41:55');
INSERT INTO `purchase_order` VALUES (17, 'PO2026000017', 23195.00, 3, '2025-12-09 10:11:41', '2025-12-19', NULL, 6, NULL, 0, '2025-12-09 10:11:41', '2026-05-06 19:41:55');
INSERT INTO `purchase_order` VALUES (18, 'PO2026000018', 10957.00, 1, '2024-01-10 05:46:31', '2024-01-18', NULL, 3, NULL, 0, '2024-01-10 05:46:31', '2026-05-06 19:41:55');
INSERT INTO `purchase_order` VALUES (19, 'PO2026000019', 356006.00, 4, '2025-07-12 04:15:48', '2025-07-23', '2025-07-20', 2, NULL, 0, '2025-07-12 04:15:48', '2026-05-06 19:41:55');
INSERT INTO `purchase_order` VALUES (20, 'PO2026000020', 92060.00, 5, '2024-11-15 01:49:01', '2024-11-26', NULL, 4, NULL, 0, '2024-11-15 01:49:01', '2026-05-06 19:41:56');
INSERT INTO `purchase_order` VALUES (21, 'PO2026000021', 10007.00, 4, '2025-10-08 07:54:48', '2025-10-17', '2025-10-18', 6, NULL, 0, '2025-10-08 07:54:48', '2026-05-06 19:41:56');
INSERT INTO `purchase_order` VALUES (22, 'PO2026000022', 45206.00, 1, '2024-01-14 15:37:06', '2024-01-27', NULL, 3, NULL, 0, '2024-01-14 15:37:06', '2026-05-06 19:41:56');
INSERT INTO `purchase_order` VALUES (23, 'PO2026000023', 59912.00, 4, '2024-08-28 15:41:32', '2024-09-09', '2024-09-08', 6, NULL, 0, '2024-08-28 15:41:32', '2026-05-06 19:41:56');
INSERT INTO `purchase_order` VALUES (24, 'PO2026000024', 60790.00, 4, '2024-05-15 13:55:09', '2024-05-22', '2024-05-19', 12, NULL, 0, '2024-05-15 13:55:09', '2026-05-06 19:41:56');
INSERT INTO `purchase_order` VALUES (25, 'PO2026000025', 132998.00, 1, '2024-11-21 10:48:18', '2024-11-29', NULL, 9, NULL, 0, '2024-11-21 10:48:18', '2026-05-06 19:41:57');
INSERT INTO `purchase_order` VALUES (26, 'PO2026000026', 37299.00, 2, '2025-12-28 17:43:44', '2026-01-13', NULL, 6, NULL, 0, '2025-12-28 17:43:44', '2026-05-06 19:41:57');
INSERT INTO `purchase_order` VALUES (27, 'PO2026000027', 128364.00, 3, '2024-12-09 02:22:26', '2024-12-17', NULL, 4, NULL, 0, '2024-12-09 02:22:26', '2026-05-06 19:41:57');
INSERT INTO `purchase_order` VALUES (28, 'PO2026000028', 21280.00, 2, '2024-07-04 14:51:13', '2024-07-16', NULL, 12, NULL, 0, '2024-07-04 14:51:13', '2026-05-06 19:41:57');
INSERT INTO `purchase_order` VALUES (29, 'PO2026000029', 59744.00, 4, '2024-02-18 07:52:54', '2024-03-03', '2024-02-29', 1, NULL, 0, '2024-02-18 07:52:54', '2026-05-06 19:41:57');
INSERT INTO `purchase_order` VALUES (30, 'PO2026000030', 62640.00, 1, '2024-11-12 04:56:29', '2024-12-01', NULL, 9, NULL, 0, '2024-11-12 04:56:29', '2026-05-06 19:41:58');
INSERT INTO `purchase_order` VALUES (31, 'PO2026000031', 36867.00, 3, '2024-07-02 04:06:58', '2024-07-14', NULL, 5, NULL, 0, '2024-07-02 04:06:58', '2026-05-06 19:41:58');
INSERT INTO `purchase_order` VALUES (32, 'PO2026000032', 110852.00, 3, '2025-11-09 07:21:39', '2025-11-28', NULL, 9, NULL, 0, '2025-11-09 07:21:39', '2026-05-06 19:41:58');
INSERT INTO `purchase_order` VALUES (33, 'PO2026000033', 48136.00, 3, '2025-01-13 11:53:19', '2025-01-23', NULL, 7, NULL, 0, '2025-01-13 11:53:19', '2026-05-06 19:41:58');
INSERT INTO `purchase_order` VALUES (34, 'PO2026000034', 71121.00, 4, '2024-02-10 02:31:26', '2024-02-28', '2024-03-02', 3, NULL, 0, '2024-02-10 02:31:26', '2026-05-06 19:41:58');
INSERT INTO `purchase_order` VALUES (35, 'PO2026000035', 147571.00, 4, '2025-01-20 17:07:39', '2025-02-05', '2025-02-02', 11, NULL, 0, '2025-01-20 17:07:39', '2026-05-06 19:41:59');
INSERT INTO `purchase_order` VALUES (36, 'PO2026000036', 73522.00, 4, '2024-03-13 05:21:43', '2024-04-01', '2024-04-03', 3, NULL, 0, '2024-03-13 05:21:43', '2026-05-06 19:41:59');
INSERT INTO `purchase_order` VALUES (37, 'PO2026000037', 55729.00, 3, '2025-03-21 02:21:07', '2025-04-06', NULL, 5, NULL, 0, '2025-03-21 02:21:07', '2026-05-06 19:41:59');
INSERT INTO `purchase_order` VALUES (38, 'PO2026000038', 90199.00, 3, '2024-03-08 02:23:00', '2024-03-27', NULL, 7, NULL, 0, '2024-03-08 02:23:00', '2026-05-06 19:41:59');
INSERT INTO `purchase_order` VALUES (39, 'PO2026000039', 35560.00, 3, '2025-12-26 19:23:28', '2026-01-02', NULL, 9, NULL, 0, '2025-12-26 19:23:28', '2026-05-06 19:41:59');
INSERT INTO `purchase_order` VALUES (40, 'PO2026000040', 64050.00, 3, '2025-01-25 22:07:28', '2025-02-11', NULL, 7, NULL, 0, '2025-01-25 22:07:28', '2026-05-06 19:41:59');
INSERT INTO `purchase_order` VALUES (41, 'PO2026000041', 97788.00, 4, '2025-12-17 16:54:25', '2025-12-30', '2026-01-01', 2, NULL, 0, '2025-12-17 16:54:25', '2026-05-06 19:41:59');
INSERT INTO `purchase_order` VALUES (42, 'PO2026000042', 16137.00, 3, '2024-12-21 02:56:26', '2025-01-09', NULL, 8, NULL, 0, '2024-12-21 02:56:26', '2026-05-06 19:41:59');
INSERT INTO `purchase_order` VALUES (43, 'PO2026000043', 120158.00, 2, '2025-07-17 08:16:49', '2025-07-28', NULL, 10, NULL, 0, '2025-07-17 08:16:49', '2026-05-06 19:41:59');
INSERT INTO `purchase_order` VALUES (44, 'PO2026000044', 88376.00, 4, '2025-01-01 07:59:42', '2025-01-19', '2025-01-21', 12, NULL, 0, '2025-01-01 07:59:42', '2026-05-06 19:41:59');
INSERT INTO `purchase_order` VALUES (45, 'PO2026000045', 18269.00, 1, '2025-01-11 09:10:11', '2025-01-31', NULL, 12, NULL, 0, '2025-01-11 09:10:11', '2026-05-06 19:42:00');
INSERT INTO `purchase_order` VALUES (46, 'PO2026000046', 7962.00, 3, '2025-09-18 16:15:03', '2025-09-27', NULL, 3, NULL, 0, '2025-09-18 16:15:03', '2026-05-06 19:42:00');
INSERT INTO `purchase_order` VALUES (47, 'PO2026000047', 8352.00, 2, '2025-02-24 06:11:48', '2025-03-15', NULL, 1, NULL, 0, '2025-02-24 06:11:48', '2026-05-06 19:42:00');
INSERT INTO `purchase_order` VALUES (48, 'PO2026000048', 84542.00, 4, '2024-11-03 04:31:14', '2024-11-21', '2024-11-19', 8, NULL, 0, '2024-11-03 04:31:14', '2026-05-06 19:42:00');
INSERT INTO `purchase_order` VALUES (49, 'PO2026000049', 68936.00, 4, '2024-08-02 09:59:49', '2024-08-22', '2024-08-25', 4, NULL, 0, '2024-08-02 09:59:49', '2026-05-06 19:42:00');
INSERT INTO `purchase_order` VALUES (50, 'PO2026000050', 10568.00, 2, '2025-05-07 08:45:56', '2025-05-15', NULL, 6, NULL, 0, '2025-05-07 08:45:56', '2026-05-06 19:42:00');
INSERT INTO `purchase_order` VALUES (51, 'PO2026000051', 155446.00, 4, '2025-08-08 07:51:55', '2025-08-17', '2025-08-15', 4, NULL, 0, '2025-08-08 07:51:55', '2026-05-06 19:42:00');
INSERT INTO `purchase_order` VALUES (52, 'PO2026000052', 164761.00, 4, '2025-04-13 02:15:19', '2025-05-03', '2025-05-02', 5, NULL, 0, '2025-04-13 02:15:19', '2026-05-06 19:42:00');
INSERT INTO `purchase_order` VALUES (53, 'PO2026000053', 44162.00, 3, '2025-06-26 05:46:54', '2025-07-11', NULL, 7, NULL, 0, '2025-06-26 05:46:54', '2026-05-06 19:42:00');
INSERT INTO `purchase_order` VALUES (54, 'PO2026000054', 68510.00, 3, '2025-04-04 09:08:44', '2025-04-23', NULL, 11, NULL, 0, '2025-04-04 09:08:44', '2026-05-06 19:42:01');
INSERT INTO `purchase_order` VALUES (55, 'PO2026000055', 71710.00, 4, '2024-04-19 02:47:52', '2024-05-07', '2024-05-07', 12, NULL, 0, '2024-04-19 02:47:52', '2026-05-06 19:42:01');
INSERT INTO `purchase_order` VALUES (56, 'PO2026000056', 9004.00, 2, '2024-12-26 16:04:39', '2025-01-06', NULL, 5, NULL, 0, '2024-12-26 16:04:39', '2026-05-06 19:42:01');
INSERT INTO `purchase_order` VALUES (57, 'PO2026000057', 8925.00, 3, '2025-05-13 05:55:26', '2025-06-01', NULL, 3, NULL, 0, '2025-05-13 05:55:26', '2026-05-06 19:42:01');
INSERT INTO `purchase_order` VALUES (58, 'PO2026000058', 176287.00, 4, '2025-05-14 18:35:35', '2025-05-27', '2025-05-29', 9, NULL, 0, '2025-05-14 18:35:35', '2026-05-06 19:42:01');
INSERT INTO `purchase_order` VALUES (59, 'PO2026000059', 47549.00, 4, '2024-08-20 19:32:40', '2024-08-31', '2024-09-03', 1, NULL, 0, '2024-08-20 19:32:40', '2026-05-06 19:42:01');
INSERT INTO `purchase_order` VALUES (60, 'PO2026000060', 6700.00, 4, '2024-06-17 10:38:35', '2024-07-06', '2024-07-08', 12, NULL, 0, '2024-06-17 10:38:35', '2026-05-06 19:42:01');
INSERT INTO `purchase_order` VALUES (61, 'PO2026000061', 5704.00, 5, '2024-07-24 11:17:38', '2024-08-06', NULL, 9, NULL, 0, '2024-07-24 11:17:38', '2026-05-06 19:42:01');
INSERT INTO `purchase_order` VALUES (62, 'PO2026000062', 40347.00, 3, '2024-10-22 13:23:24', '2024-11-11', NULL, 9, NULL, 0, '2024-10-22 13:23:24', '2026-05-06 19:42:01');
INSERT INTO `purchase_order` VALUES (63, 'PO2026000063', 124750.00, 3, '2024-06-03 17:22:07', '2024-06-17', NULL, 12, NULL, 0, '2024-06-03 17:22:07', '2026-05-06 19:42:01');
INSERT INTO `purchase_order` VALUES (64, 'PO2026000064', 10204.00, 3, '2025-01-04 01:10:11', '2025-01-12', NULL, 1, NULL, 0, '2025-01-04 01:10:11', '2026-05-06 19:42:02');
INSERT INTO `purchase_order` VALUES (65, 'PO2026000065', 12747.00, 2, '2024-04-26 06:11:34', '2024-05-11', NULL, 7, NULL, 0, '2024-04-26 06:11:34', '2026-05-06 19:42:02');
INSERT INTO `purchase_order` VALUES (66, 'PO20260506466', 0.00, 2, '2026-05-06 23:23:44', NULL, NULL, NULL, 'mcp_client 测试-仅更新状态和备注', NULL, NULL, NULL);
INSERT INTO `purchase_order` VALUES (67, 'PO2026000067', 10153.00, 5, '2025-09-08 19:57:32', '2025-09-25', NULL, 1, NULL, 0, '2025-09-08 19:57:32', '2026-05-06 19:42:02');
INSERT INTO `purchase_order` VALUES (68, 'PO2026000068', 145524.00, 4, '2025-08-25 19:09:11', '2025-09-01', '2025-09-02', 7, NULL, 0, '2025-08-25 19:09:11', '2026-05-06 19:42:02');
INSERT INTO `purchase_order` VALUES (69, 'PO2026000069', 14058.00, 2, '2024-06-18 06:11:16', '2024-06-27', NULL, 6, NULL, 0, '2024-06-18 06:11:16', '2026-05-06 19:42:02');
INSERT INTO `purchase_order` VALUES (70, 'PO2026000070', 75585.00, 4, '2025-12-06 05:04:53', '2025-12-16', '2025-12-14', 11, NULL, 0, '2025-12-06 05:04:53', '2026-05-06 19:42:02');
INSERT INTO `purchase_order` VALUES (71, 'PO2026000071', 195648.00, 4, '2024-07-24 16:08:27', '2024-08-06', '2024-08-03', 2, NULL, 0, '2024-07-24 16:08:27', '2026-05-06 19:42:02');
INSERT INTO `purchase_order` VALUES (72, 'PO2026000072', 163954.00, 2, '2025-05-08 15:52:30', '2025-05-25', NULL, 8, NULL, 0, '2025-05-08 15:52:30', '2026-05-06 19:42:03');
INSERT INTO `purchase_order` VALUES (73, 'PO2026000073', 8471.00, 5, '2024-03-06 22:33:15', '2024-03-16', NULL, 10, NULL, 0, '2024-03-06 22:33:15', '2026-05-06 19:42:03');
INSERT INTO `purchase_order` VALUES (74, 'PO2026000074', 64154.00, 4, '2025-06-28 10:20:50', '2025-07-18', '2025-07-21', 12, NULL, 0, '2025-06-28 10:20:50', '2026-05-06 19:42:03');
INSERT INTO `purchase_order` VALUES (75, 'PO2026000075', 117983.00, 1, '2024-12-15 04:58:07', '2024-12-28', NULL, 2, NULL, 0, '2024-12-15 04:58:07', '2026-05-06 19:42:03');
INSERT INTO `purchase_order` VALUES (76, 'PO2026000076', 62606.00, 3, '2024-06-18 06:21:28', '2024-06-30', NULL, 5, NULL, 0, '2024-06-18 06:21:28', '2026-05-06 19:42:03');
INSERT INTO `purchase_order` VALUES (77, 'PO2026000077', 9391.00, 3, '2024-01-24 02:15:07', '2024-02-12', NULL, 9, NULL, 0, '2024-01-24 02:15:07', '2026-05-06 19:42:04');
INSERT INTO `purchase_order` VALUES (78, 'PO2026000078', 208838.00, 4, '2024-11-01 07:21:52', '2024-11-15', '2024-11-13', 2, NULL, 0, '2024-11-01 07:21:52', '2026-05-06 19:42:04');
INSERT INTO `purchase_order` VALUES (79, 'PO2026000079', 56089.00, 1, '2024-12-19 06:20:36', '2025-01-07', NULL, 11, NULL, 0, '2024-12-19 06:20:36', '2026-05-06 19:42:05');
INSERT INTO `purchase_order` VALUES (80, 'PO2026000080', 104818.00, 4, '2025-02-17 22:20:22', '2025-02-28', '2025-03-03', 2, NULL, 0, '2025-02-17 22:20:22', '2026-05-06 19:42:05');
INSERT INTO `purchase_order` VALUES (81, 'PO2026000081', 51701.00, 3, '2024-10-24 17:13:57', '2024-11-10', NULL, 9, NULL, 0, '2024-10-24 17:13:57', '2026-05-06 19:42:05');
INSERT INTO `purchase_order` VALUES (82, 'PO2026000082', 125721.00, 4, '2025-09-17 17:24:15', '2025-09-28', '2025-09-28', 3, NULL, 0, '2025-09-17 17:24:15', '2026-05-06 19:42:05');
INSERT INTO `purchase_order` VALUES (83, 'PO2026000083', 104339.00, 4, '2024-05-27 03:16:05', '2024-06-06', '2024-06-09', 3, NULL, 0, '2024-05-27 03:16:05', '2026-05-06 19:42:05');
INSERT INTO `purchase_order` VALUES (84, 'PO2026000084', 76022.00, 4, '2024-06-27 09:10:47', '2024-07-12', '2024-07-10', 6, NULL, 0, '2024-06-27 09:10:47', '2026-05-06 19:42:05');
INSERT INTO `purchase_order` VALUES (85, 'PO2026000085', 62826.00, 2, '2025-04-04 21:22:30', '2025-04-20', NULL, 11, NULL, 0, '2025-04-04 21:22:30', '2026-05-06 19:42:05');
INSERT INTO `purchase_order` VALUES (86, 'PO2026000086', 17888.00, 4, '2025-11-11 21:33:36', '2025-11-27', '2025-11-27', 6, NULL, 0, '2025-11-11 21:33:36', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (87, 'PO2026000087', 87354.00, 2, '2024-04-15 00:08:37', '2024-05-01', NULL, 1, NULL, 0, '2024-04-15 00:08:37', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (88, 'PO2026000088', 215979.00, 3, '2025-02-07 21:51:10', '2025-02-19', NULL, 3, NULL, 0, '2025-02-07 21:51:10', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (89, 'PO2026000089', 119745.00, 3, '2025-05-10 22:10:47', '2025-05-27', NULL, 9, NULL, 0, '2025-05-10 22:10:47', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (90, 'PO2026000090', 26327.00, 3, '2025-09-11 17:55:27', '2025-09-24', NULL, 1, NULL, 0, '2025-09-11 17:55:27', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (91, 'PO2026000091', 42090.00, 1, '2024-12-23 06:52:36', '2025-01-06', NULL, 9, NULL, 0, '2024-12-23 06:52:36', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (92, 'PO2026000092', 15128.00, 3, '2024-04-09 08:03:53', '2024-04-23', NULL, 1, NULL, 0, '2024-04-09 08:03:53', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (93, 'PO2026000093', 22244.00, 1, '2024-08-08 10:07:15', '2024-08-15', NULL, 12, NULL, 0, '2024-08-08 10:07:15', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (94, 'PO2026000094', 26018.00, 2, '2025-10-11 05:09:35', '2025-10-31', NULL, 12, NULL, 0, '2025-10-11 05:09:35', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (95, 'PO2026000095', 19302.00, 3, '2025-05-13 00:28:15', '2025-05-31', NULL, 12, NULL, 0, '2025-05-13 00:28:15', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (96, 'PO2026000096', 16523.00, 2, '2025-02-28 19:46:26', '2025-03-11', NULL, 6, NULL, 0, '2025-02-28 19:46:26', '2026-05-06 19:42:06');
INSERT INTO `purchase_order` VALUES (97, 'PO2026000097', 145207.00, 3, '2024-09-06 14:46:55', '2024-09-16', NULL, 11, NULL, 0, '2024-09-06 14:46:55', '2026-05-06 19:42:07');
INSERT INTO `purchase_order` VALUES (98, 'PO2026000098', 121193.00, 1, '2025-06-13 09:17:44', '2025-07-01', NULL, 3, NULL, 0, '2025-06-13 09:17:44', '2026-05-06 19:42:07');
INSERT INTO `purchase_order` VALUES (99, 'PO2026000099', 16229.00, 4, '2025-12-03 05:00:05', '2025-12-19', '2025-12-18', 6, NULL, 0, '2025-12-03 05:00:05', '2026-05-06 19:42:07');
INSERT INTO `purchase_order` VALUES (100, 'PO2026000100', 52416.00, 3, '2024-08-18 21:44:36', '2024-08-30', NULL, 5, NULL, 0, '2024-08-18 21:44:36', '2026-05-06 19:42:07');
INSERT INTO `purchase_order` VALUES (101, 'PO2026000101', 51697.00, 3, '2024-01-03 23:42:33', '2024-01-15', NULL, 7, NULL, 0, '2024-01-03 23:42:33', '2026-05-06 19:42:07');
INSERT INTO `purchase_order` VALUES (102, 'PO2026000102', 262102.00, 3, '2024-01-07 08:59:02', '2024-01-15', NULL, 4, NULL, 0, '2024-01-07 08:59:02', '2026-05-06 19:42:07');
INSERT INTO `purchase_order` VALUES (103, 'PO2026000103', 10920.00, 4, '2025-08-27 01:38:59', '2025-09-03', '2025-09-03', 5, NULL, 0, '2025-08-27 01:38:59', '2026-05-06 19:42:07');
INSERT INTO `purchase_order` VALUES (104, 'PO2026000104', 115144.00, 3, '2024-02-22 07:13:52', '2024-03-07', NULL, 10, NULL, 0, '2024-02-22 07:13:52', '2026-05-06 19:42:07');
INSERT INTO `purchase_order` VALUES (105, 'PO2026000105', 35817.00, 3, '2024-09-02 14:03:08', '2024-09-09', NULL, 6, NULL, 0, '2024-09-02 14:03:08', '2026-05-06 19:42:07');
INSERT INTO `purchase_order` VALUES (106, 'PO2026000106', 137152.00, 1, '2024-03-12 17:38:49', '2024-03-25', NULL, 12, NULL, 0, '2024-03-12 17:38:49', '2026-05-06 19:42:08');
INSERT INTO `purchase_order` VALUES (107, 'PO2026000107', 183617.00, 3, '2025-03-25 05:14:17', '2025-04-05', NULL, 12, NULL, 0, '2025-03-25 05:14:17', '2026-05-06 19:42:08');
INSERT INTO `purchase_order` VALUES (108, 'PO2026000108', 149785.00, 3, '2024-06-27 04:12:09', '2024-07-09', NULL, 12, NULL, 0, '2024-06-27 04:12:09', '2026-05-06 19:42:08');
INSERT INTO `purchase_order` VALUES (109, 'PO2026000109', 88297.00, 1, '2024-11-19 14:53:57', '2024-12-04', NULL, 2, NULL, 0, '2024-11-19 14:53:57', '2026-05-06 19:42:08');
INSERT INTO `purchase_order` VALUES (110, 'PO2026000110', 103376.00, 5, '2024-05-02 09:21:09', '2024-05-17', NULL, 8, NULL, 0, '2024-05-02 09:21:09', '2026-05-06 19:42:08');
INSERT INTO `purchase_order` VALUES (111, 'PO2026000111', 100138.00, 1, '2025-08-17 03:16:55', '2025-09-06', NULL, 1, NULL, 0, '2025-08-17 03:16:55', '2026-05-06 19:42:08');
INSERT INTO `purchase_order` VALUES (112, 'PO2026000112', 128345.00, 4, '2024-12-07 18:14:35', '2024-12-19', '2024-12-18', 9, NULL, 0, '2024-12-07 18:14:35', '2026-05-06 19:42:08');
INSERT INTO `purchase_order` VALUES (113, 'PO2026000113', 48852.00, 4, '2024-10-13 22:29:00', '2024-11-02', '2024-10-31', 11, NULL, 0, '2024-10-13 22:29:00', '2026-05-06 19:42:08');
INSERT INTO `purchase_order` VALUES (114, 'PO2026000114', 15212.00, 4, '2025-08-05 05:35:54', '2025-08-17', '2025-08-17', 3, NULL, 0, '2025-08-05 05:35:54', '2026-05-06 19:42:08');
INSERT INTO `purchase_order` VALUES (115, 'PO2026000115', 18240.00, 4, '2024-10-17 22:02:18', '2024-10-26', '2024-10-25', 7, NULL, 0, '2024-10-17 22:02:18', '2026-05-06 19:42:08');
INSERT INTO `purchase_order` VALUES (116, 'PO2026000116', 62461.00, 4, '2025-12-15 02:42:58', '2025-12-23', '2025-12-26', 10, NULL, 0, '2025-12-15 02:42:58', '2026-05-06 19:42:09');
INSERT INTO `purchase_order` VALUES (117, 'PO2026000117', 107058.00, 4, '2024-03-08 13:24:11', '2024-03-16', '2024-03-17', 8, NULL, 0, '2024-03-08 13:24:11', '2026-05-06 19:42:09');
INSERT INTO `purchase_order` VALUES (118, 'PO2026000118', 45521.00, 1, '2025-08-06 02:55:55', '2025-08-13', NULL, 4, NULL, 0, '2025-08-06 02:55:55', '2026-05-06 19:42:09');
INSERT INTO `purchase_order` VALUES (119, 'PO2026000119', 83868.00, 5, '2025-10-19 18:24:41', '2025-10-31', NULL, 9, NULL, 0, '2025-10-19 18:24:41', '2026-05-06 19:42:09');
INSERT INTO `purchase_order` VALUES (120, 'PO2026000120', 6024.00, 3, '2025-12-17 06:00:45', '2025-12-26', NULL, 8, NULL, 0, '2025-12-17 06:00:45', '2026-05-06 19:42:09');
INSERT INTO `purchase_order` VALUES (121, 'PO202401010055', 1580.00, 1, '2026-05-06 21:29:25', '2024-01-15', NULL, NULL, '紧急采购', NULL, NULL, NULL);
INSERT INTO `purchase_order` VALUES (122, 'PO20260506101', 2615136.22, 2, '2026-05-06 23:23:44', NULL, NULL, NULL, 'mcp_client 测试订单', NULL, NULL, NULL);
INSERT INTO `purchase_order` VALUES (123, 'PO20260506257', 458840.62, 1, '2026-05-06 23:25:22', NULL, NULL, NULL, 'agent_client 模拟测试订单', NULL, NULL, NULL);
INSERT INTO `purchase_order` VALUES (124, 'PO2024010001-5977', 3742.00, 1, '2024-01-01 10:40:00', '2024-01-09', NULL, 1, '2024年1月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (125, 'PO2024010002-6096', 3070.00, 1, '2024-01-18 14:17:00', '2024-01-25', NULL, 1, '2024年1月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (126, 'PO2024010003-6125', 640.00, 1, '2024-01-19 12:26:00', '2024-01-28', NULL, 1, '2024年1月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (127, 'PO2024010004-6144', 2602.00, 2, '2024-01-16 08:23:00', '2024-01-24', NULL, 1, '2024年1月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (128, 'PO2024020005-6166', 1840.00, 2, '2024-02-20 16:14:00', '2024-03-03', NULL, 1, '2024年2月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (129, 'PO2024020006-6189', 1798.00, 2, '2024-02-28 08:42:00', '2024-03-08', NULL, 1, '2024年2月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (130, 'PO2024020007-6209', 672.00, 2, '2024-02-20 16:55:00', '2024-03-01', NULL, 1, '2024年2月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (131, 'PO2024030008-6227', 1152.00, 2, '2024-03-25 15:48:00', '2024-04-03', NULL, 1, '2024年3月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (132, 'PO2024030009-6250', 992.00, 3, '2024-03-13 09:47:00', '2024-03-20', NULL, 1, '2024年3月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (133, 'PO2024030010-6272', 3160.00, 3, '2024-03-15 10:36:00', '2024-03-22', NULL, 1, '2024年3月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (134, 'PO2024030011-6296', 2914.00, 3, '2024-03-14 14:33:00', '2024-03-22', NULL, 1, '2024年3月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (135, 'PO2024040012-6317', 480.00, 3, '2024-04-17 09:30:00', '2024-04-28', NULL, 1, '2024年4月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (136, 'PO2024040013-6362', 2592.00, 4, '2024-04-23 12:30:00', '2024-05-02', '2024-05-01', 1, '2024年4月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (137, 'PO2024040014-6385', 3378.00, 4, '2024-04-18 16:59:00', '2024-04-29', '2024-05-01', 1, '2024年4月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (138, 'PO2024050015-6420', 754.00, 4, '2024-05-13 10:18:00', '2024-05-23', '2024-05-25', 1, '2024年5月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (139, 'PO2024050016-6443', 3964.00, 4, '2024-05-07 13:58:00', '2024-05-16', '2024-05-18', 1, '2024年5月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (140, 'PO2024050017-6472', 1520.00, 4, '2024-05-26 13:18:00', '2024-06-02', '2024-06-01', 1, '2024年5月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (141, 'PO2024060018-6494', 544.00, 4, '2024-06-27 10:52:00', '2024-07-10', '2024-07-09', 1, '2024年6月火花塞常规采购订单', 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `purchase_order` VALUES (142, 'PO2024060019-6513', 1488.00, 4, '2024-06-22 13:40:00', '2024-06-29', '2024-06-29', 1, '2024年6月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (143, 'PO2024070020-6536', 3528.00, 4, '2024-07-16 10:33:00', '2024-07-26', '2024-07-25', 1, '2024年7月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (144, 'PO2024070021-6563', 3446.00, 4, '2024-07-05 15:56:00', '2024-07-12', '2024-07-11', 1, '2024年7月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (145, 'PO2024080022-6589', 4046.00, 4, '2024-08-08 09:32:00', '2024-08-20', '2024-08-22', 1, '2024年8月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (146, 'PO2024080023-6617', 3596.00, 4, '2024-08-19 14:31:00', '2024-08-29', '2024-08-30', 1, '2024年8月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (147, 'PO2024080024-6641', 2562.00, 4, '2024-08-04 11:27:00', '2024-08-17', '2024-08-18', 1, '2024年8月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (148, 'PO2024080025-6664', 1640.00, 4, '2024-08-01 17:17:00', '2024-08-13', '2024-08-12', 1, '2024年8月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (149, 'PO2024090026-6689', 2524.00, 4, '2024-09-04 15:50:00', '2024-09-17', '2024-09-19', 1, '2024年9月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (150, 'PO2024090027-6709', 3854.00, 4, '2024-09-13 13:27:00', '2024-09-20', '2024-09-19', 1, '2024年9月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (151, 'PO2024090028-6729', 1248.00, 4, '2024-09-19 14:45:00', '2024-10-02', '2024-10-01', 1, '2024年9月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (152, 'PO2024100029-6746', 2616.00, 4, '2024-10-28 16:30:00', '2024-11-08', '2024-11-07', 1, '2024年10月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (153, 'PO2024100030-6790', 1520.00, 4, '2024-10-28 10:09:00', '2024-11-04', '2024-11-02', 1, '2024年10月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (154, 'PO2024100031-6811', 800.00, 4, '2024-10-06 17:34:00', '2024-10-14', '2024-10-13', 1, '2024年10月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (155, 'PO2024110032-6835', 448.00, 4, '2024-11-15 10:59:00', '2024-11-28', '2024-11-29', 1, '2024年11月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (156, 'PO2024110033-6856', 1416.00, 4, '2024-11-28 13:08:00', '2024-12-06', '2024-12-05', 1, '2024年11月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (157, 'PO2024110034-6882', 1520.00, 4, '2024-11-19 16:22:00', '2024-11-26', '2024-11-27', 1, '2024年11月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (158, 'PO2024120035-6903', 3168.00, 4, '2024-12-26 09:38:00', '2025-01-04', '2025-01-06', 1, '2024年12月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (159, 'PO2024120036-6922', 1040.00, 4, '2024-12-08 12:22:00', '2024-12-18', '2024-12-20', 1, '2024年12月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (160, 'PO2024120037-6940', 544.00, 4, '2024-12-28 15:06:00', '2025-01-04', '2025-01-02', 1, '2024年12月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (161, 'PO2024120038-6958', 704.00, 4, '2024-12-08 11:35:00', '2024-12-18', '2024-12-16', 1, '2024年12月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (162, 'PO2025010001-6989', 1560.00, 4, '2025-01-02 12:05:00', '2025-01-14', '2025-01-12', 1, '2025年1月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (163, 'PO2025010002-7011', 1080.00, 4, '2025-01-28 17:13:00', '2025-02-09', '2025-02-07', 1, '2025年1月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (164, 'PO2025010003-7038', 736.00, 4, '2025-01-10 17:24:00', '2025-01-18', '2025-01-18', 1, '2025年1月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (165, 'PO2025010004-7057', 1920.00, 4, '2025-01-11 11:34:00', '2025-01-21', '2025-01-19', 1, '2025年1月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (166, 'PO2025020005-7087', 1440.00, 4, '2025-02-18 09:24:00', '2025-03-03', '2025-03-04', 1, '2025年2月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (167, 'PO2025020006-7134', 3344.00, 4, '2025-02-08 13:39:00', '2025-02-17', '2025-02-17', 1, '2025年2月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (168, 'PO2025020007-7162', 800.00, 4, '2025-02-02 14:05:00', '2025-02-09', '2025-02-09', 1, '2025年2月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (169, 'PO2025030008-7183', 2010.00, 4, '2025-03-13 13:01:00', '2025-03-21', '2025-03-21', 1, '2025年3月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (170, 'PO2025030009-7206', 2686.00, 4, '2025-03-23 10:49:00', '2025-04-01', '2025-04-02', 1, '2025年3月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (171, 'PO2025030010-7225', 2906.00, 4, '2025-03-22 11:34:00', '2025-03-30', '2025-03-28', 1, '2025年3月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (172, 'PO2025030011-7249', 2754.00, 4, '2025-03-10 12:53:00', '2025-03-20', '2025-03-21', 1, '2025年3月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (173, 'PO2025030012-7267', 4234.00, 4, '2025-03-16 16:35:00', '2025-03-28', '2025-03-27', 1, '2025年3月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (174, 'PO2025040013-7288', 638.00, 4, '2025-04-08 15:02:00', '2025-04-20', '2025-04-18', 1, '2025年4月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (175, 'PO2025040014-7309', 2224.00, 4, '2025-04-03 16:29:00', '2025-04-12', '2025-04-14', 1, '2025年4月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (176, 'PO2025040015-7330', 1586.00, 4, '2025-04-26 13:36:00', '2025-05-08', '2025-05-10', 1, '2025年4月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (177, 'PO2025040016-7349', 2960.00, 4, '2025-04-03 15:31:00', '2025-04-14', '2025-04-14', 1, '2025年4月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (178, 'PO2025050017-7375', 2098.00, 3, '2025-05-16 11:03:00', '2025-05-29', NULL, 1, '2025年5月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (179, 'PO2025050018-7396', 384.00, 4, '2025-05-24 17:57:00', '2025-06-06', '2025-06-04', 1, '2025年5月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (180, 'PO2025050019-7415', 3024.00, 1, '2025-05-20 15:44:00', '2025-06-01', NULL, 1, '2025年5月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (181, 'PO2025050020-7436', 3208.00, 4, '2025-05-16 12:15:00', '2025-05-26', '2025-05-28', 1, '2025年5月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');
INSERT INTO `purchase_order` VALUES (182, 'PO2025050021-7458', 2788.00, 3, '2025-05-03 09:22:00', '2025-05-12', NULL, 1, '2025年5月火花塞常规采购订单', 0, '2026-05-09 12:30:37', '2026-05-09 12:30:37');

-- ----------------------------
-- Table structure for supplier
-- ----------------------------
DROP TABLE IF EXISTS `supplier`;
CREATE TABLE `supplier`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT '供应商ID',
  `supplier_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '供应商编码',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '供应商名称',
  `contact_person` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '联系人',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '联系电话',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '邮箱',
  `address` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '地址',
  `credit_rating` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'B' COMMENT '信用评级',
  `status` tinyint(0) NULL DEFAULT 1 COMMENT '合作状态',
  `deleted` tinyint(0) NULL DEFAULT 0 COMMENT '删除标志',
  `create_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `update_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_supplier_code`(`supplier_code`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 34 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '供应商表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of supplier
-- ----------------------------
INSERT INTO `supplier` VALUES (1, 'SUP00001', '博世汽车配件（上海）有限公司', '联系人J', '13858772272', 'supplier1@motorparts.com', '上海市嘉定区安亭镇汽车城某路1号', 'D', 2, 0, '2024-07-02 23:21:38', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (2, 'SUP00002', '电装（上海）国际贸易有限公司', '联系人M', '13859157074', 'supplier2@motorparts.com', '上海市嘉定区安亭镇汽车城某路2号', 'B', 1, 0, '2024-01-27 13:19:31', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (3, 'SUP00003', '布雷博制动系统有限公司', '联系人D', '13837607001', 'supplier3@motorparts.com', '上海市嘉定区安亭镇汽车城某路3号', 'B', 3, 0, '2025-04-22 21:49:39', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (4, 'SUP00004', '昭和자동차株弍会社上海代表处', '联系人H', '13882107665', 'supplier4@motorparts.com', '上海市嘉定区安亭镇汽车城某路4号', 'A', 1, 0, '2024-11-04 13:48:58', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (5, 'SUP00005', 'KYB（中国）投资有限公司', '联系人V', '13891272838', 'supplier5@motorparts.com', '上海市嘉定区安亭镇汽车城某路5号', 'A', 2, 0, '2025-05-12 08:18:05', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (6, 'SUP00006', '日清纺油脂（上海）有限公司', '联系人O', '13858374245', 'supplier6@motorparts.com', '上海市嘉定区安亭镇汽车城某路6号', 'B', 1, 0, '2025-09-03 12:34:22', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (7, 'SUP00007', '米其林（中国）投资有限公司', '联系人R', '13863242867', 'supplier7@motorparts.com', '上海市嘉定区安亭镇汽车城某路7号', 'A', 1, 0, '2025-11-12 04:11:11', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (8, 'SUP00008', '倍耐力轮胎有限公司', '联系人R', '13824318543', 'supplier8@motorparts.com', '上海市嘉定区安亭镇汽车城某路8号', 'B', 1, 0, '2024-06-17 13:02:14', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (9, 'SUP00009', '普利司通（上海）国际贸易有限公司', '联系人W', '13890127275', 'supplier9@motorparts.com', '上海市嘉定区安亭镇汽车城某路9号', 'A', 1, 0, '2025-12-10 06:59:20', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (10, 'SUP00010', '固特异（大连）轮胎有限公司', '联系人D', '13866000763', 'supplier10@motorparts.com', '上海市嘉定区安亭镇汽车城某路10号', 'A', 3, 0, '2024-11-14 00:43:23', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (11, 'SUP00011', '博格华纳汽车配件（宁波）有限公司', '联系人E', '13822337110', 'supplier11@motorparts.com', '上海市嘉定区安亭镇汽车城某路11号', 'B', 1, 0, '2024-07-26 01:06:10', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (12, 'SUP00012', '采埃孚汽车系统（上海）有限公司', '联系人I', '13824608835', 'supplier12@motorparts.com', '上海市嘉定区安亭镇汽车城某路12号', 'A', 1, 0, '2024-10-13 18:00:25', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (13, 'SUP00013', '大陆汽车投资（上海）有限公司', '联系人U', '13873158381', 'supplier13@motorparts.com', '上海市嘉定区安亭镇汽车城某路13号', 'C', 1, 0, '2024-08-20 13:53:29', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (14, 'SUP00014', '麦格纳汽车技术（上海）有限公司', '联系人Z', '13856704070', 'supplier14@motorparts.com', '上海市嘉定区安亭镇汽车城某路14号', 'A', 2, 0, '2024-01-24 15:34:53', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (15, 'SUP00015', '法雷奥汽车内部控制（上海）有限公司', '联系人T', '13805469956', 'supplier15@motorparts.com', '上海市嘉定区安亭镇汽车城某路15号', 'D', 3, 0, '2024-12-06 05:47:57', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (16, 'SUP00016', '德尔福汽车系统（中国）投资有限公司', '联系人E', '13884364635', 'supplier16@motorparts.com', '上海市嘉定区安亭镇汽车城某路16号', 'C', 1, 0, '2024-05-01 19:12:32', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (17, 'SUP00017', '李尔（上海）汽车饰件有限公司', '联系人Y', '13844037961', 'supplier17@motorparts.com', '上海市嘉定区安亭镇汽车城某路17号', 'C', 1, 0, '2025-10-10 22:16:04', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (18, 'SUP00018', '江森自控（上海）管理有限公司', '联系人X', '13876873220', 'supplier18@motorparts.com', '上海市嘉定区安亭镇汽车城某路18号', 'C', 1, 0, '2025-07-01 15:49:30', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (19, 'SUP00019', '天合汽车科技（上海）有限公司', '联系人A', '13879493806', 'supplier19@motorparts.com', '上海市嘉定区安亭镇汽车城某路19号', 'C', 3, 0, '2025-03-07 04:35:02', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (20, 'SUP00020', '辉门汽车配件（上海）有限公司', '联系人U', '13864064830', 'supplier20@motorparts.com', '上海市嘉定区安亭镇汽车城某路20号', 'D', 3, 0, '2025-02-11 17:34:33', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (21, 'SUP00021', '康明斯发动机（上海）国际贸易有限公司', '联系人Z', '13831140091', 'supplier21@motorparts.com', '上海市嘉定区安亭镇汽车城某路21号', 'D', 1, 0, '2024-08-28 10:07:31', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (22, 'SUP00022', '五十铃汽车工程塑料（上海）有限公司', '联系人Y', '13879752611', 'supplier22@motorparts.com', '上海市嘉定区安亭镇汽车城某路22号', 'D', 1, 0, '2025-01-15 14:05:04', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (23, 'SUP00023', '爱信精机（上海）贸易有限公司', '联系人F', '13841744640', 'supplier23@motorparts.com', '上海市嘉定区安亭镇汽车城某路23号', 'C', 3, 0, '2024-07-14 11:35:45', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (24, 'SUP00024', '捷太格特汽车配件（上海）有限公司', '联系人R', '13828880680', 'supplier24@motorparts.com', '上海市嘉定区安亭镇汽车城某路24号', 'C', 2, 0, '2024-07-10 20:15:27', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (25, 'SUP00025', '恩梯恩汽车配件（上海）有限公司', '联系人R', '13822248042', 'supplier25@motorparts.com', '上海市嘉定区安亭镇汽车城某路25号', 'C', 1, 0, '2025-08-16 21:09:51', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (26, 'SUP00026', '捷豹路虎汽车备件贸易（上海）有限公司', '联系人T', '13899735170', 'supplier26@motorparts.com', '上海市嘉定区安亭镇汽车城某路26号', 'C', 1, 0, '2025-10-12 11:03:47', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (27, 'SUP00027', '盖茨汽车配件（上海）有限公司', '联系人S', '13857853489', 'supplier27@motorparts.com', '上海市嘉定区安亭镇汽车城某路27号', 'D', 3, 0, '2024-05-08 22:38:58', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (28, 'SUP00028', '豹牌刹车片有限公司', '联系人O', '13832072489', 'supplier28@motorparts.com', '上海市嘉定区安亭镇汽车城某路28号', 'B', 1, 0, '2025-09-11 15:47:40', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (29, 'SUP00029', '马牌轮胎（上海）贸易有限公司', '联系人M', '13863437996', 'supplier29@motorparts.com', '上海市嘉定区安亭镇汽车城某路29号', 'B', 1, 0, '2025-11-04 22:00:25', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (30, 'SUP00030', '优科豪马轮胎销售有限公司', '联系人M', '13865058041', 'supplier30@motorparts.com', '上海市嘉定区安亭镇汽车城某路30号', 'D', 2, 0, '2024-11-24 11:17:00', '2026-05-06 19:41:51');
INSERT INTO `supplier` VALUES (31, 'SUP-SPARK-001', '电装配件专营店', '田中太郎', '021-88880001', 'denso@motorparts.com', '上海市嘉定区安亭镇汽车城博园路1001号', 'A', 1, 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `supplier` VALUES (32, 'SUP-SPARK-002', '博世配件旗舰店', 'Hans Mueller', '021-88880002', 'bosch@motorparts.com', '上海市浦东新区张江高科技园区碧波路690号', 'A', 1, 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');
INSERT INTO `supplier` VALUES (33, 'SUP-SPARK-003', '电气配件专营店', '山本健二', '021-88880003', 'ngk@motorparts.com', '上海市静安区南京西路1788号国际中心2001室', 'A', 1, 0, '2026-05-09 12:30:36', '2026-05-09 12:30:36');

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户名',
  `password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码(加密)',
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `role` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'purchase' COMMENT '角色',
  `department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '采购部' COMMENT '部门',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '电话',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '邮箱',
  `status` tinyint(0) NULL DEFAULT 1 COMMENT '状态',
  `deleted` tinyint(0) NULL DEFAULT 0 COMMENT '删除标志',
  `create_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `update_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_username`(`username`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户/员工表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, 'user1', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '系统管理员', 'admin', '财务部', '13839239535', 'admin@motorparts.com', 1, 0, '2026-05-06 19:41:50', '2026-05-06 19:41:50');
INSERT INTO `user` VALUES (2, 'user2', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '张三', 'purchase', '采购部', '13845270712', 'zhangsan@motorparts.com', 1, 0, '2026-05-06 19:41:50', '2026-05-06 19:41:50');
INSERT INTO `user` VALUES (3, 'user3', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '李四', 'warehouse', '仓储部', '13864035905', 'lisi@motorparts.com', 1, 0, '2026-05-06 19:41:51', '2026-05-06 19:41:51');
INSERT INTO `user` VALUES (4, 'user4', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '王五', 'sales', '销售部', '13825103027', 'wangwu@motorparts.com', 1, 0, '2026-05-06 19:41:51', '2026-05-06 19:41:51');
INSERT INTO `user` VALUES (5, 'user5', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '赵六', 'admin', '财务部', '13878514981', 'zhaoliu@motorparts.com', 1, 0, '2026-05-06 19:41:51', '2026-05-06 19:41:51');
INSERT INTO `user` VALUES (6, 'user6', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '钱七', 'purchase', '采购部', '13896769044', 'qianqi@motorparts.com', 1, 0, '2026-05-06 19:41:51', '2026-05-06 19:41:51');
INSERT INTO `user` VALUES (7, 'user7', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '孙八', 'warehouse', '仓储部', '13815978356', 'sunba@motorparts.com', 1, 0, '2026-05-06 19:41:51', '2026-05-06 19:41:51');
INSERT INTO `user` VALUES (8, 'user8', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '周九', 'sales', '销售部', '13821953353', 'zhoujiu@motorparts.com', 1, 0, '2026-05-06 19:41:51', '2026-05-06 19:41:51');
INSERT INTO `user` VALUES (9, 'user9', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '系统管理员2', 'admin', '财务部', '13864498014', 'admin@motorparts.com', 1, 0, '2026-05-06 19:41:51', '2026-05-06 19:41:51');
INSERT INTO `user` VALUES (10, 'user10', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '张三2', 'purchase', '采购部', '13821225762', 'zhangsan@motorparts.com', 1, 0, '2026-05-06 19:41:51', '2026-05-06 19:41:51');
INSERT INTO `user` VALUES (11, 'user11', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '李四2', 'warehouse', '仓储部', '13837370560', 'lisi@motorparts.com', 1, 0, '2026-05-06 19:41:51', '2026-05-06 19:41:51');
INSERT INTO `user` VALUES (12, 'user12', '$2a$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '王五2', 'sales', '销售部', '13875048320', 'wangwu@motorparts.com', 1, 0, '2026-05-06 19:41:51', '2026-05-06 19:41:51');

SET FOREIGN_KEY_CHECKS = 1;
