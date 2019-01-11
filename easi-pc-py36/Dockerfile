FROM ubuntu:latest

LABEL maintainer="CSIRO EASI Data Cube Training on PC <Robert.Woodcock@csiro.au>"

USER root

# A littel apt configuration to speed downloads a little
ADD 99parallel /etc/apt/apt.conf.d/99parallel

# Switch to Australian mirror for ubuntu apt packages, add NextGIS repo and update existing packages for security and patching
# This is the updated base OS layer
RUN sed --in-place --regexp-extended "s/(\/\/)(archive\.ubuntu)/\1au.\2/" /etc/apt/sources.list && \
	apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:nextgis/ppa && \
    apt-get upgrade --yes

ENV DEBIAN_FRONTEND noninteractive

# Install core requirements for ODC development and jupyter notebooks
RUN apt-get install -y --no-install-recommends \
    # Core requirements
    gdal-bin gdal-data libgdal-dev libgdal20 libudunits2-0 \
    # Extra python components, to speed things up
    python3 python3-setuptools python3-dev \
    python3-numpy python3-netcdf4 python3-gdal \
    # Need pip to install more python packages later.
    # The libdpkg-perl is needed to build pyproj
    python3-pip python3-wheel libdpkg-perl \
    # Git to work out the ODC version number
    git \
    # G++ because GDAL decided it needed compiling
    g++ \
    # numpy requires headers for cf_units
    libudunits2-dev \
    # Additional utilities useful for ODC dev
	postgresql-client \
	curl \
    wget \
    bzip2 \
    ca-certificates \
    sudo \
    locales \
    fonts-liberation \
    ffmpeg \
    # OS dependencies for fully functional Jupyter notebook server as listed on the jupyter docker stacks
    # Most art commented out as they seem unnecessary for the current training evironment and keep the docker container build and size smaller
    build-essential \
    # emacs \
    # inkscape \
    # jed \
    # libsm6 \
    # libxext-dev \
    # libxrender1 \
    # lmodern \
    # netcat \
    # pandoc \
    # texlive-fonts-extra \
    # texlive-fonts-recommended \
    # texlive-generic-recommended \
    # texlive-latex-base \
    # texlive-latex-extra \
    # texlive-xetex \
    unzip \
    nano \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure Jupyter Notebook
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Configure environment
ENV SHELL=/bin/bash \
    NB_USER=jovyan \
    NB_UID=1000 \
    NB_GID=100 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
ENV HOME=/home/$NB_USER

ADD fix-permissions /usr/local/bin/fix-permissions
# Create jovyan user with UID=1000 and in the 'users' group
# and make sure these dirs are writable by the `users` group.
RUN groupadd wheel -g 11 && \
    echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
    useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
    chmod g+w /etc/passwd && \
    /bin/bash fix-permissions $HOME && \
# Install Tini.. this is required because CMD (below) doesn't play nice with notebooks for some reason: https://github.com/ipython/ipython/issues/7062, https://github.com/jupyter/notebook/issues/334
    curl -L https://github.com/krallin/tini/releases/download/v0.10.0/tini > tini && \
    echo "1361527f39190a7338a0b434bd8c88ff7233ce7b9a4876f3315c22fce7eca1b0 *tini" | sha256sum -c - && \
    mv tini /usr/local/bin/tini && \
    chmod +x /usr/local/bin/tini

USER $NB_UID

# Setup work directory for backward-compatibility
RUN mkdir $HOME/work && \
    mkdir $HOME/odc && \
    /bin/bash fix-permissions $HOME && \
# Install psycopg2 as a special case, to quiet the warning message 
    pip3 install --no-cache --no-binary :all: psycopg2 && \
# Install jupyter notebook and additional python packages for interactive odc use
    pip3 install jupyter matplotlib folium ffmpeg shapely scikit-image

USER root

EXPOSE 8888

# Configure container startup
ENTRYPOINT ["/usr/local/bin/tini", "-g", "--"]

# launch notebook
CMD ["/bin/bash", "start-notebook.sh"]

# Add local files as late as possible to avoid cache busting
COPY start.sh /usr/local/bin/
COPY start-notebook.sh /usr/local/bin/
COPY jupyter_notebook_config.py /etc/jupyter/
RUN /bin/bash fix-permissions /etc/jupyter/
RUN chmod +x /usr/local/bin/start.sh /usr/local/bin/start-notebook.sh

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

