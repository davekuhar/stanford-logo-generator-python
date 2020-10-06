# Stanford Logo Generator
Project Notes

Fonts:
- install in `~/.fonts` or `/usr/share/fonts/truetype[/font_name]`
- location under /usr/share/fonts/truetype doesn't matter: fc-cache recurses down the full tree
- `sudo fc-cache -f` to rebuild the index
- `fc-list` to see the rebuilt font list

```
# to set up AMI on Ubuntu:
sudo apt-get update
sudo apt-get upgrade -y
sudo add-apt-repository ppa:inkscape.dev/stable -y
sudo apt-get update  # installs to /usr/bin/inkscape
sudo apt-get install inkscape -y
sudo apt-get install python-pip -y
sudo apt-get install uuid-dev libcap.dev libpcre3-dev
sudo apt install imagemagick
```

Install python3 utils
`$ sudo apt install python3-distutils -y`
`$ sudo apt-get install python3-dev`

Install unzip package
`$ sudo apt-get install -y unzip`

Extract zip to /var/www/html/api
`$ sudo unzip api.zip -d /var/www/html/api`

Install virtualenv 
`sudo apt install virtualenv`

Make virtualenv
`$ virtualenv venv`

Activate virtualenv
`$ source venv/bin/activate`

Install requirements
`(venv) $ pip install -r requirements.txt`


Deactivate virtualenv
`(venv) $ deactivate`

Setup gunicorn socket
`$ sudo cp gunicorn.socket /etc/systemd/system/gunicorn.socket`

Setup gunicorn service
`sudo cp gunicorn.service /etc/systemd/system/gunicorn.service`

Start gunicorn socket
`$ sudo systemctl start gunicorn.socket`

Enable gunicorn socket
`$ sudo systemctl enable gunicorn.socket`

Install Apache2
`$ sudo apt install apache2`

Copy Apache2 config
`$ cp api.apache.conf /etc/apache2/sites-enabled/api.conf`

Enable api configurationg
`$ sudo a2ensite api.conf`

Restart Apache2 Service
`$ sudo systemctl reload apache2`



Install nginx
`$ sudo apt install nginx`


Copy nginx config template to server
`cp api.nginx.conf  /etc/nginx/sites-available/api`


Remove default nginx site config
`sudo rm /etc/nginx/sites-enabled/default `


Enable nginx site
`$ sudo ln -S /etc/nginx/sites-available/api /etc/nginx/sites-enabled/default`

    
Restart nginx
`$ sudo service nginx restart`

The api can acceesed at
`http://server_domain_or_IP/api/v1/`

To restart the api
`sudo service gunicorn restart`