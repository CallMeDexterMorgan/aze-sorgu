-- 🔍 AZE Sorgu Panel - Sagird.sql
-- GitHub: https://raw.githubusercontent.com/knk/aze-sorgu/main/sagird.sql

DROP TABLE IF EXISTS `sagirdler`;
CREATE TABLE `sagirdler` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ad_soyad` varchar(100) NOT NULL,
  `sagird_no` varchar(20) NOT NULL,
  `utis_kod` varchar(20) NOT NULL,
  `sinif` varchar(10) NOT NULL,
  `mekteb` varchar(150) NOT NULL,
  `telefon` varchar(20) NOT NULL,
  `unvan` text NOT NULL,
  `qeydiyyat_ili` year(4) NOT NULL,
  `valideyn` varchar(100) DEFAULT NULL,
  `valideyn_telefon` varchar(20) DEFAULT NULL,
  `qeyd` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sagird_no` (`sagird_no`),
  UNIQUE KEY `utis_kod` (`utis_kod`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sagird məlumatları
INSERT INTO `sagirdler` (`id`, `ad_soyad`, `sagird_no`, `utis_kod`, `sinif`, `mekteb`, `telefon`, `unvan`, `qeydiyyat_ili`) VALUES
(1, 'Əliyev Elnur', '2023001', 'UTIS12345', '11A', 'Bakı şəhəri 162 nömrəli tam orta məktəb', '+994501234567', 'Bakı, Nərimanov rayonu, N.Nərimanov prospekti 45', '2023'),
(2, 'Məmmədova Aygün', '2023042', 'UTIS54321', '9B', 'Sumqayıt şəhəri 6 nömrəli tam orta məktəb', '+994507654321', 'Sumqayıt, 8-ci mikrorayon, ev 34', '2023'),
(3, 'Həsənov Rəşad', '2022115', 'UTIS78901', '12C', 'Gəncə şəhəri 1 nömrəli lisey', '+994553339988', 'Gəncə, Kəpəz rayonu, H.Əliyev prospekti 78', '2022'),
(4, 'Quliyeva Ləman', '2023088', 'UTIS98765', '10A', 'Xırdalan şəhəri 3 nömrəli tam orta məktəb', '+994703332211', 'Abşeron rayonu, Xırdalan, Müşfiq küçəsi 12', '2023'),
(5, 'Tağıyev Nicat', '2021177', 'UTIS45678', '11B', 'Bakı şəhəri 23 nömrəli tam orta məktəb', '+994552223344', 'Bakı, Yasamal rayonu, M.Şəhriyar küçəsi 56', '2021'),
(6, 'Rzayeva Zəhra', '2023099', 'UTIS11223', '9C', 'Bakı Avropa Liseyi', '+994505556677', 'Bakı, Xətai rayonu, Nobel prospekti 89', '2023'),
(7, 'Səlimov Tural', '2022055', 'UTIS44556', '10C', 'Mingəçevir şəhəri 4 nömrəli tam orta məktəb', '+994517778899', 'Mingəçevir, S.Vurğun küçəsi 23', '2022'),
(8, 'Kərimova Fatimə', '2023100', 'UTIS99887', '8A', 'Bakı Türk Liseyi', '+994501112233', 'Bakı, Nəsimi rayonu, C.Cabbarlı küçəsi 15', '2023'),
(9, 'Abdullayev Rəhman', '2022150', 'UTIS33456', '11C', 'Bakı şəhəri 5 nömrəli məktəb', '+994507778899', 'Bakı, Səbail rayonu, Neftçilər prospekti 67', '2022'),
(10, 'Hüseynova Lalə', '2023101', 'UTIS44567', '9A', 'Bakı Qızlar Liseyi', '+994553334455', 'Bakı, Nərimanov, Təbriz küçəsi 34', '2023');

-- View yaradılması
CREATE VIEW `sagird_aktiv` AS
SELECT * FROM `sagirdler` WHERE `qeydiyyat_ili` >= 2023;

-- Index optimizasiyası
CREATE INDEX `idx_ad_soyad` ON `sagirdler`(`ad_soyad`);
CREATE INDEX `idx_sagird_no` ON `sagirdler`(`sagird_no`);
CREATE INDEX `idx_utis` ON `sagirdler`(`utis_kod`);
CREATE INDEX `idx_telefon` ON `sagirdler`(`telefon`);
