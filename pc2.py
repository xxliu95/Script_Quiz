#!/usr/bin/python
# Alumnos:
# Xinxin Liu
# Fco. Romulo Ballero Garijo
from subprocess import call
import os

# Instalacion del escenario
def escenario():
    os.chdir("/mnt/tmp") # Para el laboratorio
    call("wget http://idefix.dit.upm.es/cdps/pc2/pc2.tgz", shell=True)
    call("sudo vnx --unpack pc2.tgz", shell=True)
    os.chdir("pc2")
    call("sudo vnx -f pc2.xml --destroy", shell=True) # Para empezar limpio
    call("bin/prepare-pc2-vm", shell=True)
    call("sudo vnx -f pc2.xml --create", shell=True)

# Configuracion del firewall
def fw():
    call("sudo /lab/cdps/bin/cp2lxc /home/xinxin.liu/Desktop/fw.fw /var/lib/lxc/fw/rootfs", shell=True) # Hay que poner la ruta absoluta de fw
    call("sudo lxc-attach --clear-env -n fw -- chmod +x fw.fw ", shell=True)
    call("sudo lxc-attach --clear-env -n fw -- bash -c \"./fw.fw\"",shell=True)


# Configuracion de la base de datos
def ddbb():
    call("sudo lxc-attach --clear-env -n bbdd -- apt update", shell=True)
    call("sudo lxc-attach --clear-env -n bbdd -- apt -y install mariadb-server", shell=True)
    call("sudo lxc-attach --clear-env -n bbdd -- sed -i -e 's/bind.address.*/bind-address=0.0.0.0/' -e 's/utf8mb4/utf8/' /etc/mysql/mariadb.conf.d/50-server.cnf", shell=True)
    call("sudo lxc-attach --clear-env -n bbdd -- systemctl restart mysql",shell=True)
    call("sudo lxc-attach --clear-env -n bbdd -- mysqladmin -u root password xxxx",shell=True)
    call("sudo lxc-attach --clear-env -n bbdd -- mysql -u root --password='xxxx' -e \"CREATE USER 'quiz' IDENTIFIED BY 'xxxx' ; \"",shell=True)
    call("sudo lxc-attach --clear-env -n bbdd -- mysql -u root --password='xxxx' -e \"CREATE DATABASE quiz;\"",shell=True)
    call("sudo lxc-attach --clear-env -n bbdd -- mysql -u root --password='xxxx' -e \"GRANT ALL PRIVILEGES ON quiz.* to 'quiz'@'localhost' IDENTIFIED by 'xxxx' ;\"",shell=True)
    call("sudo lxc-attach --clear-env -n bbdd -- mysql -u root --password='xxxx' -e \"GRANT ALL PRIVILEGES ON quiz.* to 'quiz'@'%' IDENTIFIED by 'xxxx' ;\"",shell=True)
    call("sudo lxc-attach --clear-env -n bbdd -- mysql -u root --password='xxxx' -e \"FLUSH PRIVILEGES;\"",shell=True)

# Configuracion de glusterf
def glusterf():
    cmd_line = "sudo lxc-attach --clear-env -n nas1 -- bash -c \" 	\
		          gluster peer probe 20.20.4.22;\
                  gluster peer probe 20.20.4.23;\
                  gluster volume create nas replica 3 20.20.4.21:/nas 20.20.4.22:/nas 20.20.4.23:/nas force;\
                  gluster volume start nas;\
                  gluster volume set nas network.ping-timeout 5\" "
    call(cmd_line,shell=True)
    call("sudo lxc-attach --clear-env -n nas2 -- gluster volume set nas network.ping-timeout 5",shell=True)
    call("sudo lxc-attach --clear-env -n nas3 -- gluster volume set nas network.ping-timeout 5",shell=True)
    # Montado
    call("sudo lxc-attach --clear-env -n s1 -- mkdir /mnt/nas; mount -t glusterfs 20.20.4.21:/nas /mnt/nas",shell=True)
    call("sudo lxc-attach --clear-env -n s2 -- mkdir /mnt/nas; mount -t glusterfs 20.20.4.22:/nas /mnt/nas",shell=True)
    call("sudo lxc-attach --clear-env -n s3 -- mkdir /mnt/nas; mount -t glusterfs 20.20.4.23:/nas /mnt/nas",shell=True)

# Instalacion y configuracion de quiz
def quiz():
    # Actualizar npm por si acaso
    cmd_line_s1 = "sudo lxc-attach --clear-env -n s1 -- bash -c \" 				    \
        	sudo apt-get install -y npm;										    \
        	npm install npm@latest -g;												\
        	git clone https://github.com/CORE-UPM/quiz_2020.git; 					\
            cd /quiz_2020;												            \
        	npm install;															\
        	npm install forever;													\
        	npm install mysql2;														\
        	export QUIZ_OPEN_REGISTER=yes; 											\
        	export DATABASE_URL=mysql://quiz:xxxx@20.20.4.31:3306/quiz;  			\
        	npm run-script migrate_cdps;											\
        	npm run-script seed_cdps;												\
        	./node_modules/forever/bin/forever start ./bin/www \""

    cmd_line_s2 = "sudo lxc-attach --clear-env -n s2 -- bash -c \" 				    \
        	sudo apt-get install -y npm;										    \
        	npm install npm@latest -g;												\
        	git clone https://github.com/CORE-UPM/quiz_2020.git; 					\
            cd /quiz_2020;												            \
        	npm install;															\
        	npm install forever;													\
        	npm install mysql2;														\
        	export QUIZ_OPEN_REGISTER=yes; 											\
        	export DATABASE_URL=mysql://quiz:xxxx@20.20.4.31:3306/quiz;  			\
        	./node_modules/forever/bin/forever start ./bin/www \""

    cmd_line_s3 = "sudo lxc-attach --clear-env -n s3 -- bash -c \" 				    \
        	sudo apt-get install -y npm;										    \
        	npm install npm@latest -g;												\
        	git clone https://github.com/CORE-UPM/quiz_2020.git; 					\
            cd /quiz_2020;												            \
        	npm install;															\
        	npm install forever;													\
        	npm install mysql2;														\
        	export QUIZ_OPEN_REGISTER=yes; 											\
        	export DATABASE_URL=mysql://quiz:xxxx@20.20.4.31:3306/quiz;  			\
        	./node_modules/forever/bin/forever start ./bin/www \""

    call(cmd_line_s1,shell=True)
    call(cmd_line_s2,shell=True)
    call(cmd_line_s3,shell=True)

    call("sudo lxc-attach --clear-env -n s1 -- bash -c \"echo 'S1'>/quiz_2020/views/index.ejs \"",shell=True)
    call("sudo lxc-attach --clear-env -n s2 -- bash -c \"echo 'S2'>/quiz_2020/views/index.ejs \"",shell=True)
    call("sudo lxc-attach --clear-env -n s3 -- bash -c \"echo 'S3'>/quiz_2020/views/index.ejs \"",shell=True)

    # Enlace simbolico a los servidores NAS
    call(" sudo lxc-attach --clear-env -n s1 -- bash -c \"cd /quiz_2020/public; ln -s /mnt/nas uploads; \" ",shell = True)
    call(" sudo lxc-attach --clear-env -n s2 -- bash -c \"cd /quiz_2020/public; ln -s /mnt/nas uploads; \" ",shell = True)
    call(" sudo lxc-attach --clear-env -n s3 -- bash -c \"cd /quiz_2020/public; ln -s /mnt/nas uploads; \" ",shell = True)

# Configuracion del balanceador de trafico
def haproxy():
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"sudo apt-get update && sudo apt-get -y upgrade; sudo apt-get install -y haproxy\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- service apache2 stop",shell=True) # Hay que para apache primero
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"echo 'frontend lb'>> /etc/haproxy/haproxy.cfg\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"echo ' bind *:80'>> /etc/haproxy/haproxy.cfg\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"echo ' mode http'>> /etc/haproxy/haproxy.cfg\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"echo ' default_backend webservers'>> /etc/haproxy/haproxy.cfg\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"echo 'backend webservers'>> /etc/haproxy/haproxy.cfg\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"echo ' mode http'>> /etc/haproxy/haproxy.cfg\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"echo ' balance roundrobin'>> /etc/haproxy/haproxy.cfg\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"echo ' server s1 20.20.3.11:3000 check'>> /etc/haproxy/haproxy.cfg\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"echo ' server s2 20.20.3.12:3000 check'>> /etc/haproxy/haproxy.cfg\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- bash -c \"echo ' server s3 20.20.3.13:3000 backup'>> /etc/haproxy/haproxy.cfg\"",shell=True)
    call("sudo lxc-attach --clear-env -n lb -- sudo service haproxy restart",shell=True)

# __main__
if __name__ == '__main__':
    # ejecutar todas las funciones
    escenario()
    fw()
    ddbb()
    glusterf()
    quiz()
    haproxy()
