# JP
## nginxをインストール（amazon-linux-2バージョン）
- nginx repo を有効させる
- yum でインストール
> ansible の yum モジュールがパッケージの有無をチェックしてくれる（既にインストールされていたら状態を変更しない）

## 参考
- [AnsibleでEC2のAmazon Linux 2にNginxをインストールする方法の検討](https://qiita.com/3244/items/051a2c44e19ab932dc0f)

# EN
## Install nginx (For amazon-linux-2)
- enable nginx repo to install using yum
> user can't install nginx using yum by default in amazon-linux-2, so we enable it using shell module and silent the changed state

- install nginx with yum
> let yum module to decide if it is installed so that it can tell ansible if we changed the state in the instance

## Reference
- [How to check and install nginx in amazon-linux-2 (JP)](https://qiita.com/3244/items/051a2c44e19ab932dc0f)