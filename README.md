# 会社寮光熱費計算アプリ
> [tl-calculator.christeena0717.me](https://tl-calculator.christeena0717.me)

## 背景
- 自分は会社の寮に住んでいます。
- 寮は11部屋の一軒家ですが、なぜか電気メーターが6個しかない。
- 5部屋は各自のメーターで、残りの部屋と共用スペースはシェアという感じです。
- そのうえ、従業員の使用頻度（日数）もみなそれぞれですので、毎月光熱費を計算するのを苦労してました。
- そのため、自動的に計算してくれるアプリを作りたいと決めました。

## 使用ツール
今回は、完全自動化構築を目指しているため、いくつのツールを使用しました。
1. [CircleCI](README.md#circleci)：   GitHubと連携して、ソースコードを読み込んで、インフラから、アプリ設定まで、構築してくれる
2. [Terraform](README.md#Terraform)：  アプリの基盤になるインフラを構築するためのツール、今回はAWSにて構築
3. [Ansible](README.md#Ansible)：    リモートで、AWSに作ったEC2にアクセスして、アプリを設定する

### CircleCI
- githubにpushすると、自動的に<code>config.yml</code>を基づいて構築するようになります。
- 今回のブランチ分岐は、CircleCIのパイプラインのブランチでgitのブランチを参照して分岐しています
- なので開発環境(dev)と本番環境(prod)の環境変数もCircleCIのプロジェクトコンフィグ(project config)で設定します

### Terraform
- <code>main.tf</code>の中にリソースを設定
- 今回はmoduleを使わなかったのは、単純に個人的に1ページ化のコンフィグが好きです
- ページの中に<code>ctrl+F</code>で探したいものをすぐ見つかるため、他のフォルダーに他のモジュールを探すより手間が省けます
- 必要な部分だけ（output、variables）を別ファイルに分けます
- 構築した後にoutputをjsonフォーマットで保存して、後のAnsibleに渡します

### Ansible
- <code>playbook.yml</code>で、Terraformで構築したサーバのEC2にsshしてアプリを注入します
- もともとAnsibleではhostの指定は必要ですが、今回は完全自動構築ですので、最初からhostのipがわからない状態です
- なのでTerraformが構築した後に吐き出した<code>output.json</code>を、Ansibleが利用します
  - パスワードなどはCircleCIの環境変数にて設定してありますので、stdoutにプリントされてもマスクされます（CircleCI環境変数document参照）
- DjangoやNginxなどを設定して、発動しましたら完成です

## インフラストラクチャー（AWS)
### インフラ構成図
![Environment (my portfolio)](https://user-images.githubusercontent.com/103508472/204108145-12e982d0-0a80-4d03-af4a-d337468af981.jpg)


## アプリ

### 依存ソフトウェア/Dependencies
- Python 3.10.4
- Django 4.1.1
- django-cors-headers 3.13.0
- mysql-client 0.0.1
- PyMySQL 1.0.2
- uWSGI 2.0.20

### アプリ概要
- Django MVC
- 基本CRUD処理

### 基本機能
- 光熱費と部屋住民のデータ入力（CREATE）
- 住民データ更新（UPDATE）
- 光熱費照会（READ）
- 住民データ照会（READ）
- 光熱費データ削除（DELETE）

### 使用技術
- フロントエンド
  - bootstrap 5.0
  - django template
  - html/css/js

- バックエンド
  - Python
  - Django
  - uwsgi
  - NGINX
  
## DB ダイアグラム
![Database diagram](https://user-images.githubusercontent.com/103508472/194231389-1c9906c9-32c5-46b9-bb40-31b90ccb0734.jpg)
