FROM jenkins/jenkins:2.568.3-jdk21
COPY plugins.txt plugins.lock.txt /usr/share/jenkins/ref/
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.lock.txt
COPY casc.yaml /usr/share/jenkins/ref/casc.yaml
ENV CASC_JENKINS_CONFIG=/usr/share/jenkins/ref/casc.yaml
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
