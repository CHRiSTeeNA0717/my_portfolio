# JP
## 会社寮光熱費計算アプリ
> [tl-calculator.christeena0717.me](tl-calculator.christeena0717.me)

### 背景
- 自分は会社の寮に住んでいます。
- 寮は11部屋の一軒家ですが、なぜか電気メーターが6個しかない。
- 5部屋は各自のメーターで、残りの部屋と共用スペースはシェアという感じです。
- そのうえ、従業員の使用頻度（日数）もみなそれぞれですので、毎月光熱費を計算するのを苦労してました。
- そのため、自動的に計算してくれるアプリを作りたいと決めました。


## 依存ソフトウェア
- Python 3.10.4
- Django 4.1.1
- django-cors-headers 3.13.0
- mysql-client 0.0.1
- PyMySQL 1.0.2
- uWSGI 2.0.20

## アプリ概要
- Django MVC
- 基本CRUD処理

## 基本機能
- 光熱費と部屋住民のデータ入力（CREATE）
- 住民データ更新（UPDATE）
- 光熱費照会（READ）
- 住民データ照会（READ）
- 光熱費データ削除（DELETE）

## 使用技術
### フロントエンド
- bootstrap 5.0
- django template
- html/css/js

### バックエンド
- Python
- Django
- uwsgi
- NGINX

### インフラストラクチャー
- ROUTE 53
- AWS VPC
  - EC2
  - ALB
- AWS RDS
  - MySQL
  
## DB ダイアグラム
![Database diagram](https://user-images.githubusercontent.com/103508472/194231389-1c9906c9-32c5-46b9-bb40-31b90ccb0734.jpg)

## インフラ構成図
![Environment](https://user-images.githubusercontent.com/103508472/194231467-6b20be28-149f-4e79-8ffc-a58302c274e0.jpg)


# ENG
## App to auto calculate bills for company dormitory
> [tl-calculator.christeena0717.me](tl-calculator.christeena0717.me)

## Dependencies
- Python 3.10.4
- Django 4.1.1
- django-cors-headers 3.13.0
- mysql-client 0.0.1
- PyMySQL 1.0.2
- uWSGI 2.0.20

## App Summary
- Django MVC
- CRUD process

## Basic usage
- New bill data, room data input（CREATE）
- room data update（UPDATE）
- bill data output（READ）
- room data output（READ）
- bill data deletion（DELETE）

## Skills
### Frontend
- bootstrap 5.0
- django template
- html/css/js

### Backend
- Python
- Django
- uwsgi
- NGINX

### Infrastructure
- ROUTE 53
- AWS VPC
  - EC2
  - ALB
- AWS RDS
  - MySQL
  
## DB Diagram
![Database diagram](https://user-images.githubusercontent.com/103508472/194231389-1c9906c9-32c5-46b9-bb40-31b90ccb0734.jpg)

## Infrastructure Config Diagram
![Environment](https://user-images.githubusercontent.com/103508472/194231467-6b20be28-149f-4e79-8ffc-a58302c274e0.jpg)
