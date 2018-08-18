ALTER TABLE `xcmarket`.`xcm_vxn_currency_info` 
CHANGE COLUMN `currency` `currency` VARCHAR(20) NOT NULL COMMENT '币种' ,
CHANGE COLUMN `fullname` `fullname` VARCHAR(45) NOT NULL COMMENT '币种全名' ,
CHANGE COLUMN `cnname` `cnname` VARCHAR(45) NOT NULL COMMENT '币种中文名' ,
CHANGE COLUMN `description` `description` VARCHAR(45) NULL DEFAULT NULL COMMENT '币种描述' ,
CHANGE COLUMN `create_time` `create_time` INT(11) NULL DEFAULT NULL COMMENT '加入时间' ,
CHANGE COLUMN `update_time` `update_time` INT(11) NULL DEFAULT NULL COMMENT '更新时间' ;
