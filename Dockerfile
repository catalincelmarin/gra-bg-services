# syntax=docker/dockerfile:1
FROM python:3.12-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
#     nodejs \
#     npm \
    vim \
    sudo \
    cron \
    procps \
    curl \
    lsof \
    ntpdate \
    git \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Clean up apt cache to keep image slim
# Create a user with a home directory
RUN useradd -ms /bin/bash jazzms

# Set password for the user
RUN echo 'jazzms:no!way?jos3' | chpasswd
# Add the user to the sudo group
RUN usermod -aG sudo jazzms

# Allow the user to run sudo commands without password prompt
RUN echo 'jazzms ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Set the working directory to the user's home directory
WORKDIR /home/jazzms
# Set up environment variables
ENV PATH="/home/jazzms/.local/bin:${PATH}"
# Set up Poetry environment variables for virtualenv location
ENV POETRY_VIRTUALENVS_CREATE=true
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
# Creates the virtualenv inside the project folder

USER jazzms

RUN curl -sSL https://install.python-poetry.org | python3 -
# Copy the project files
COPY ./README.md README.md
COPY ./.env .env

# Declare build-time arguments
COPY ./_pyproject.toml pyproject.toml
#COPY poetry.lock poetry.lock
COPY ./app /home/jazzms/app

# Set file permissions for the app
RUN sudo chmod -R 0777 /home/jazzms/app/logs/
RUN sudo chmod -R 0777 /etc/ssl/
# RUN sudo chmod -R 0777 /home/jazzms/poetry.lock
ARG API_GITHUB
# Set environment variables in the container
# ENV API_GITHUB=${API_GITHUB}
RUN export GITHUB_API=${API_GITHUB} && \
    echo "https://$GITHUB_API@github.com" > /home/jazzms/.git-credentials && \
    git config --global credential.helper store

# Set up the virtual environment and install dependencies using Poetry
# RUN poetry lock --no-update
RUN poetry install --no-interaction --no-ansi
#RUN poetry run playwright install chromium
#RUN poetry run playwright install-deps
RUN poetry build

# Set up crontab for the app
COPY ./app/bin/crontab /etc/cron.d/ms-cron
RUN sudo chmod 0644 /etc/cron.d/ms-cron
RUN sudo crontab /etc/cron.d/ms-cron

# Copy and set up entrypoint script
COPY ./up.sh /tmp/up.sh
RUN sudo mv /tmp/up.sh /usr/local/bin/up.sh && sudo chmod +x /usr/local/bin/up.sh

RUN sudo ntpdate -s time.nist.gov
# Reload sysctl settings to apply the changes immediately
RUN sysctl -p

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/up.sh"]
