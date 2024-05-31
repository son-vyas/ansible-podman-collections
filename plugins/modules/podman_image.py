#!/usr/bin/python
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
  module: podman_image
  author:
      - Sam Doran (@samdoran)
  short_description: Pull images for use by podman
  notes: []
  description:
      - Build, pull, or push images using Podman.
  options:
    arch:
      description:
        - CPU architecture for the container image
      type: str
    name:
      description:
        - Name of the image to pull, push, or delete. It may contain a tag using the format C(image:tag).
      required: True
      type: str
    executable:
      description:
        - Path to C(podman) executable if it is not in the C($PATH) on the machine running C(podman).
      default: 'podman'
      type: str
    ca_cert_dir:
      description:
        - Path to directory containing TLS certificates and keys to use.
      type: 'path'
    tag:
      description:
        - Tag of the image to pull, push, or delete.
      default: "latest"
      type: str
    pull:
      description: Whether or not to pull the image.
      default: True
      type: bool
    pull_extra_args:
      description:
        - Extra arguments to pass to the pull command.
      type: str
    push:
      description: Whether or not to push an image.
      default: False
      type: bool
    path:
      description: Path to the build context directory.
      type: str
    force:
      description:
        - Whether or not to force push or pull an image.
        - When building, force the build even if the image already exists.
      type: bool
      default: False
    state:
      description:
        - Whether an image should be present, absent, or built.
      default: "present"
      type: str
      choices:
        - present
        - absent
        - build
        - quadlet
    validate_certs:
      description:
        - Require HTTPS and validate certificates when pulling or pushing. Also used during build if a pull or push is necessary.
      type: bool
      aliases:
        - tlsverify
        - tls_verify
    password:
      description:
        - Password to use when authenticating to remote registries.
      type: str
    username:
      description:
        - username to use when authenticating to remote registries.
      type: str
    auth_file:
      description:
        - Path to file containing authorization credentials to the remote registry.
      aliases:
        - authfile
      type: path
    build:
      description: Arguments that control image build.
      type: dict
      default: {}
      aliases:
        - build_args
        - buildargs
      suboptions:
        file:
          description:
            - Path to the Containerfile if it is not in the build context directory.
          type: path
        volume:
          description:
            - Specify multiple volume / mount options to mount one or more mounts to a container.
          type: list
          elements: str
        annotation:
          description:
            - Dictionary of key=value pairs to add to the image. Only works with OCI images. Ignored for Docker containers.
          type: dict
        force_rm:
          description:
            - Always remove intermediate containers after a build, even if the build is unsuccessful.
          type: bool
          default: False
        format:
          description:
            - Format of the built image.
          type: str
          choices:
            - docker
            - oci
          default: "oci"
        cache:
          description:
            - Whether or not to use cached layers when building an image
          type: bool
          default: True
        rm:
          description: Remove intermediate containers after a successful build
          type: bool
          default: True
        extra_args:
          description:
            - Extra args to pass to build, if executed. Does not idempotently check for new build args.
          type: str
        target:
          description:
            - Specify the target build stage to build.
          type: str
    push_args:
      description: Arguments that control pushing images.
      type: dict
      default: {}
      suboptions:
        compress:
          description:
            - Compress tarball image layers when pushing to a directory using the 'dir' transport.
          type: bool
        format:
          description:
            - Manifest type to use when pushing an image using the 'dir' transport (default is manifest type of source).
          type: str
          choices:
            - oci
            - v2s1
            - v2s2
        remove_signatures:
          description: Discard any pre-existing signatures in the image
          type: bool
        sign_by:
          description:
            - Path to a key file to use to sign the image.
          type: str
        dest:
          description: Path or URL where image will be pushed.
          type: str
          aliases:
            - destination
        transport:
          description:
            - Transport to use when pushing in image. If no transport is set, will attempt to push to a remote registry.
          type: str
          choices:
            - dir
            - docker
            - docker-archive
            - docker-daemon
            - oci-archive
            - ostree
        extra_args:
          description:
            - Extra args to pass to push, if executed. Does not idempotently check for new push args.
          type: str
    quadlet_dir:
      description:
        - Path to the directory to write quadlet file in.
          By default, it will be set as C(/etc/containers/systemd/) for root user,
          C(~/.config/containers/systemd/) for non-root users.
      type: path
      required: false
    quadlet_filename:
      description:
        - Name of quadlet file to write. By default it takes image name without prefixes and tags.
      type: str
    quadlet_options:
      description:
        - Options for the quadlet file. Provide missing in usual network args
          options as a list of lines to add.
      type: list
      elements: str
      required: false
'''

EXAMPLES = r"""
- name: Pull an image
  containers.podman.podman_image:
    name: quay.io/bitnami/wildfly

- name: Remove an image
  containers.podman.podman_image:
    name: quay.io/bitnami/wildfly
    state: absent

- name: Remove an image with image id
  containers.podman.podman_image:
    name: 0e901e68141f
    state: absent

- name: Pull a specific version of an image
  containers.podman.podman_image:
    name: redis
    tag: 4

- name: Build a basic OCI image
  containers.podman.podman_image:
    name: nginx
    path: /path/to/build/dir

- name: Build a basic OCI image with advanced parameters
  containers.podman.podman_image:
    name: nginx
    path: /path/to/build/dir
    build:
      cache: no
      force_rm: true
      format: oci
      annotation:
        app: nginx
        function: proxy
        info: Load balancer for my cool app
      extra_args: "--build-arg KEY=value"

- name: Build a Docker formatted image
  containers.podman.podman_image:
    name: nginx
    path: /path/to/build/dir
    build:
      format: docker

- name: Build and push an image using existing credentials
  containers.podman.podman_image:
    name: nginx
    path: /path/to/build/dir
    push: true
    push_args:
      dest: quay.io/acme

- name: Build and push an image using an auth file
  containers.podman.podman_image:
    name: nginx
    push: true
    auth_file: /etc/containers/auth.json
    push_args:
      dest: quay.io/acme

- name: Build and push an image using username and password
  containers.podman.podman_image:
    name: nginx
    push: true
    username: bugs
    password: "{{ vault_registry_password }}"
    push_args:
      dest: quay.io/acme

- name: Build and push an image to multiple registries
  containers.podman.podman_image:
    name: "{{ item }}"
    path: /path/to/build/dir
    push: true
    auth_file: /etc/containers/auth.json
    loop:
    - quay.io/acme/nginx
    - docker.io/acme/nginx

- name: Build and push an image to multiple registries with separate parameters
  containers.podman.podman_image:
    name: "{{ item.name }}"
    tag: "{{ item.tag }}"
    path: /path/to/build/dir
    push: true
    auth_file: /etc/containers/auth.json
    push_args:
      dest: "{{ item.dest }}"
    loop:
    - name: nginx
      tag: 4
      dest: docker.io/acme

    - name: nginx
      tag: 3
      dest: docker.io/acme

- name: Pull an image for a specific CPU architecture
  containers.podman.podman_image:
    name: nginx
    arch: amd64

- name: Create a quadlet file for an image
  containers.podman.podman_image:
    name: docker.io/library/alpine:latest
    state: quadlet
    quadlet_dir: /etc/containers/systemd
    quadlet_filename: alpine-latest
    quadlet_options:
      - Variant=arm/v7
      - |
        [Install]
        WantedBy=default.target
"""

RETURN = r"""
  image:
    description:
      - Image inspection results for the image that was pulled, pushed, or built.
    returned: success
    type: dict
    sample: [
      {
        "Annotations": {},
        "Architecture": "amd64",
        "Author": "",
        "Comment": "from Bitnami with love",
        "ContainerConfig": {
          "Cmd": [
            "/run.sh"
          ],
          "Entrypoint": [
            "/app-entrypoint.sh"
          ],
          "Env": [
            "PATH=/opt/bitnami/java/bin:/opt/bitnami/wildfly/bin:/opt/bitnami/nami/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "IMAGE_OS=debian-9",
            "NAMI_VERSION=1.0.0-1",
            "GPG_KEY_SERVERS_LIST=ha.pool.sks-keyservers.net",
            "TINI_VERSION=v0.13.2",
            "TINI_GPG_KEY=595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7",
            "GOSU_VERSION=1.10",
            "GOSU_GPG_KEY=B42F6819007F00F88E364FD4036A9C25BF357DD4",
            "BITNAMI_IMAGE_VERSION=16.0.0-debian-9-r27",
            "BITNAMI_PKG_CHMOD=-R g+rwX",
            "BITNAMI_PKG_EXTRA_DIRS=/home/wildfly",
            "HOME=/",
            "BITNAMI_APP_NAME=wildfly",
            "NAMI_PREFIX=/.nami",
            "WILDFLY_HOME=/home/wildfly",
            "WILDFLY_JAVA_HOME=",
            "WILDFLY_JAVA_OPTS=",
            "WILDFLY_MANAGEMENT_HTTP_PORT_NUMBER=9990",
            "WILDFLY_PASSWORD=bitnami",
            "WILDFLY_PUBLIC_CONSOLE=true",
            "WILDFLY_SERVER_AJP_PORT_NUMBER=8009",
            "WILDFLY_SERVER_HTTP_PORT_NUMBER=8080",
            "WILDFLY_SERVER_INTERFACE=0.0.0.0",
            "WILDFLY_USERNAME=user",
            "WILDFLY_WILDFLY_HOME=/home/wildfly",
            "WILDFLY_WILDFLY_OPTS=-Dwildfly.as.deployment.ondemand=false"
          ],
          "ExposedPorts": {
            "8080/tcp": {},
            "9990/tcp": {}
          },
          "Labels": {
            "maintainer": "Bitnami <containers@bitnami.com>"
          },
          "User": "1001"
        },
        "Created": "2019-04-10T05:48:03.553887623Z",
        "Digest": "sha256:5a8ab28e314c2222de3feaf6dac94a0436a37fc08979d2722c99d2bef2619a9b",
        "GraphDriver": {
          "Data": {
            "LowerDir": "/var/lib/containers/storage/overlay/142c1beadf1bb09fbd929465ec98c9dca3256638220450efb4214727d0d0680e/diff:/var/lib/containers/s",
            "MergedDir": "/var/lib/containers/storage/overlay/9aa10191f5bddb59e28508e721fdeb43505e5b395845fa99723ed787878dbfea/merged",
            "UpperDir": "/var/lib/containers/storage/overlay/9aa10191f5bddb59e28508e721fdeb43505e5b395845fa99723ed787878dbfea/diff",
            "WorkDir": "/var/lib/containers/storage/overlay/9aa10191f5bddb59e28508e721fdeb43505e5b395845fa99723ed787878dbfea/work"
          },
          "Name": "overlay"
        },
        "History": [
          {
            "comment": "from Bitnami with love",
            "created": "2019-04-09T22:27:40.659377677Z"
          },
          {
            "created": "2019-04-09T22:38:53.86336555Z",
            "created_by": "/bin/sh -c #(nop)  LABEL maintainer=Bitnami <containers@bitnami.com>",
            "empty_layer": true
          },
          {
            "created": "2019-04-09T22:38:54.022778765Z",
            "created_by": "/bin/sh -c #(nop)  ENV IMAGE_OS=debian-9",
            "empty_layer": true
          },
        ],
        "Id": "ace34da54e4af2145e1ad277005adb235a214e4dfe1114c2db9ab460b840f785",
        "Labels": {
          "maintainer": "Bitnami <containers@bitnami.com>"
        },
        "ManifestType": "application/vnd.docker.distribution.manifest.v1+prettyjws",
        "Os": "linux",
        "Parent": "",
        "RepoDigests": [
          "quay.io/bitnami/wildfly@sha256:5a8ab28e314c2222de3feaf6dac94a0436a37fc08979d2722c99d2bef2619a9b"
        ],
        "RepoTags": [
          "quay.io/bitnami/wildfly:latest"
        ],
        "RootFS": {
          "Layers": [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
          ],
          "Type": "layers"
        },
        "Size": 466180019,
        "User": "1001",
        "Version": "18.09.3",
        "VirtualSize": 466180019
      }
    ]
"""

import json
import os
import re
import shlex

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.containers.podman.plugins.module_utils.podman.common import run_podman_command
from ansible_collections.containers.podman.plugins.module_utils.podman.quadlet import create_quadlet_state


class PodmanImageManager(object):

    def __init__(self, module, results):

        super(PodmanImageManager, self).__init__()

        self.module = module
        self.results = results
        self.name = self.module.params.get('name')
        self.executable = self.module.get_bin_path(module.params.get('executable'), required=True)
        self.tag = self.module.params.get('tag')
        self.pull = self.module.params.get('pull')
        self.pull_extra_args = self.module.params.get('pull_extra_args')
        self.push = self.module.params.get('push')
        self.path = self.module.params.get('path')
        self.force = self.module.params.get('force')
        self.state = self.module.params.get('state')
        self.validate_certs = self.module.params.get('validate_certs')
        self.auth_file = self.module.params.get('auth_file')
        self.username = self.module.params.get('username')
        self.password = self.module.params.get('password')
        self.ca_cert_dir = self.module.params.get('ca_cert_dir')
        self.build = self.module.params.get('build')
        self.push_args = self.module.params.get('push_args')
        self.arch = self.module.params.get('arch')

        repo, repo_tag = parse_repository_tag(self.name)
        if repo_tag:
            self.name = repo
            self.tag = repo_tag

        delimiter = ':' if "sha256" not in self.tag else '@'
        self.image_name = '{name}{d}{tag}'.format(name=self.name, d=delimiter, tag=self.tag)

        if self.state in ['present', 'build']:
            self.present()

        if self.state in ['absent']:
            self.absent()

        if self.state == 'quadlet':
            self.make_quadlet()

    def _run(self, args, expected_rc=0, ignore_errors=False):
        cmd = " ".join([self.executable]
                       + [to_native(i) for i in args])
        self.module.log("PODMAN-IMAGE-DEBUG: %s" % cmd)
        self.results['podman_actions'].append(cmd)
        return run_podman_command(
            module=self.module,
            executable=self.executable,
            args=args,
            expected_rc=expected_rc,
            ignore_errors=ignore_errors)

    def _get_id_from_output(self, lines, startswith=None, contains=None, split_on=' ', maxsplit=1):
        layer_ids = []
        for line in lines.splitlines():
            if startswith and line.startswith(startswith) or contains and contains in line:
                splitline = line.rsplit(split_on, maxsplit)
                layer_ids.append(splitline[1])

        # Podman 1.4 changed the output to only include the layer id when run in quiet mode
        if not layer_ids:
            layer_ids = lines.splitlines()

        return (layer_ids[-1])

    def present(self):
        image = self.find_image()

        if image:
            digest_before = image[0].get('Digest', image[0].get('digest'))
        else:
            digest_before = None

        if not image or self.force:
            if self.state == 'build' or self.path:
                # Build the image
                build_file = self.build.get('file') if self.build else None
                if not self.path and build_file:
                    self.path = os.path.dirname(build_file)
                elif not self.path and not build_file:
                    self.module.fail_json(msg='Path to build context or file is required when building an image')
                self.results['actions'].append('Built image {image_name} from {path}'.format(
                    image_name=self.image_name, path=self.path))
                if not self.module.check_mode:
                    self.results['image'], self.results['stdout'] = self.build_image()
                    image = self.results['image']
            else:
                # Pull the image
                self.results['actions'].append('Pulled image {image_name}'.format(image_name=self.image_name))
                if not self.module.check_mode:
                    image = self.results['image'] = self.pull_image()

            if not image:
                image = self.find_image()
            if not self.module.check_mode:
                digest_after = image[0].get('Digest', image[0].get('digest'))
                self.results['changed'] = digest_before != digest_after
            else:
                self.results['changed'] = True

        if self.push:
            self.results['image'], output = self.push_image()
            self.results['stdout'] += "\n" + output
        if image and not self.results.get('image'):
            self.results['image'] = image

    def absent(self):
        image = self.find_image()
        image_id = self.find_image_id()

        if image:
            self.results['actions'].append('Removed image {name}'.format(name=self.name))
            self.results['changed'] = True
            self.results['image']['state'] = 'Deleted'
            if not self.module.check_mode:
                self.remove_image()
        elif image_id:
            self.results['actions'].append(
                'Removed image with id {id}'.format(id=self.image_name))
            self.results['changed'] = True
            self.results['image']['state'] = 'Deleted'
            if not self.module.check_mode:
                self.remove_image_id()

    def make_quadlet(self):
        results_update = create_quadlet_state(self.module, "image")
        self.results.update(results_update)
        self.module.exit_json(**self.results)

    def find_image(self, image_name=None):
        if image_name is None:
            image_name = self.image_name
        args = ['image', 'ls', image_name, '--format', 'json']
        rc, images, err = self._run(args, ignore_errors=True)
        try:
            images = json.loads(images)
        except json.decoder.JSONDecodeError:
            self.module.fail_json(msg='Failed to parse JSON output from podman image ls: {out}'.format(out=images))
        if len(images) == 0:
            # Let's find out if image exists
            rc, out, err = self._run(['image', 'exists', image_name], ignore_errors=True)
            if rc == 0:
                inspect_json = self.inspect_image(image_name)
            else:
                return None
        if len(images) > 0:
            inspect_json = self.inspect_image(image_name)
        if self._is_target_arch(inspect_json, self.arch) or not self.arch:
            return images or inspect_json
        return None

    def _is_target_arch(self, inspect_json=None, arch=None):
        return arch and inspect_json[0]['Architecture'] == arch

    def find_image_id(self, image_id=None):
        if image_id is None:
            # If image id is set as image_name, remove tag
            image_id = re.sub(':.*$', '', self.image_name)
        args = ['image', 'ls', '--quiet', '--no-trunc']
        rc, candidates, err = self._run(args, ignore_errors=True)
        candidates = [re.sub('^sha256:', '', c)
                      for c in str.splitlines(candidates)]
        for c in candidates:
            if c.startswith(image_id):
                return image_id
        return None

    def inspect_image(self, image_name=None):
        if image_name is None:
            image_name = self.image_name
        args = ['inspect', image_name, '--format', 'json']
        rc, image_data, err = self._run(args)
        try:
            image_data = json.loads(image_data)
        except json.decoder.JSONDecodeError:
            self.module.fail_json(msg='Failed to parse JSON output from podman inspect: {out}'.format(out=image_data))
        if len(image_data) > 0:
            return image_data
        else:
            return None

    def pull_image(self, image_name=None):
        if image_name is None:
            image_name = self.image_name

        args = ['pull', image_name, '-q']

        if self.arch:
            args.extend(['--arch', self.arch])

        if self.auth_file:
            args.extend(['--authfile', self.auth_file])

        if self.username and self.password:
            cred_string = '{user}:{password}'.format(user=self.username, password=self.password)
            args.extend(['--creds', cred_string])

        if self.validate_certs is not None:
            if self.validate_certs:
                args.append('--tls-verify')
            else:
                args.append('--tls-verify=false')

        if self.ca_cert_dir:
            args.extend(['--cert-dir', self.ca_cert_dir])

        if self.pull_extra_args:
            args.extend(shlex.split(self.pull_extra_args))

        rc, out, err = self._run(args, ignore_errors=True)
        if rc != 0:
            if not self.pull:
                self.module.fail_json(msg='Failed to find image {image_name} locally, image pull set to {pull_bool}'.format(
                    pull_bool=self.pull, image_name=image_name))
            else:
                self.module.fail_json(msg='Failed to pull image {image_name}'.format(image_name=image_name))
        return self.inspect_image(out.strip())

    def build_image(self):
        args = ['build']
        args.extend(['-t', self.image_name])

        if self.validate_certs is not None:
            if self.validate_certs:
                args.append('--tls-verify')
            else:
                args.append('--tls-verify=false')

        annotation = self.build.get('annotation')
        if annotation:
            for k, v in annotation.items():
                args.extend(['--annotation', '{k}={v}'.format(k=k, v=v)])

        if self.ca_cert_dir:
            args.extend(['--cert-dir', self.ca_cert_dir])

        if self.build.get('force_rm'):
            args.append('--force-rm')

        image_format = self.build.get('format')
        if image_format:
            args.extend(['--format', image_format])

        if not self.build.get('cache'):
            args.append('--no-cache')

        if self.build.get('rm'):
            args.append('--rm')

        containerfile = self.build.get('file')
        if containerfile:
            args.extend(['--file', containerfile])

        volume = self.build.get('volume')
        if volume:
            for v in volume:
                args.extend(['--volume', v])

        if self.auth_file:
            args.extend(['--authfile', self.auth_file])

        if self.username and self.password:
            cred_string = '{user}:{password}'.format(user=self.username, password=self.password)
            args.extend(['--creds', cred_string])

        extra_args = self.build.get('extra_args')
        if extra_args:
            args.extend(shlex.split(extra_args))

        target = self.build.get('target')
        if target:
            args.extend(['--target', target])

        args.append(self.path)

        rc, out, err = self._run(args, ignore_errors=True)
        if rc != 0:
            self.module.fail_json(msg="Failed to build image {image}: {out} {err}".format(image=self.image_name, out=out, err=err))

        last_id = self._get_id_from_output(out, startswith='-->')
        return self.inspect_image(last_id), out + err

    def push_image(self):
        args = ['push']

        if self.validate_certs is not None:
            if self.validate_certs:
                args.append('--tls-verify')
            else:
                args.append('--tls-verify=false')

        if self.ca_cert_dir:
            args.extend(['--cert-dir', self.ca_cert_dir])

        if self.username and self.password:
            cred_string = '{user}:{password}'.format(user=self.username, password=self.password)
            args.extend(['--creds', cred_string])

        if self.auth_file:
            args.extend(['--authfile', self.auth_file])

        if self.push_args.get('compress'):
            args.append('--compress')

        push_format = self.push_args.get('format')
        if push_format:
            args.extend(['--format', push_format])

        if self.push_args.get('remove_signatures'):
            args.append('--remove-signatures')

        sign_by_key = self.push_args.get('sign_by')
        if sign_by_key:
            args.extend(['--sign-by', sign_by_key])

        push_extra_args = self.push_args.get('extra_args')
        if push_extra_args:
            args.extend(shlex.split(push_extra_args))

        args.append(self.image_name)

        # Build the destination argument
        dest = self.push_args.get('dest')
        transport = self.push_args.get('transport')

        if dest is None:
            dest = self.image_name

        # Append container name and tag to dest
        if '/' not in self.image_name:
            dest = f'{dest}/{self.name}:{self.tag}'
        else:
            dest = f'{dest}/{self.image_name}'

        if transport:
            if transport == 'docker':
                dest_format_string = '{transport}://{dest}'
            elif transport == 'ostree':
                dest_format_string = '{transport}:{name}@{dest}'
            else:
                dest_format_string = '{transport}:{dest}'
                if transport == 'docker-daemon' and ":" not in dest:
                    dest_format_string = '{transport}:{dest}:latest'
            dest_string = dest_format_string.format(transport=transport, name=self.name, dest=dest)
        else:
            dest_string = dest

        if "/" not in dest_string and "@" not in dest_string and "docker-daemon" not in dest_string:
            self.module.fail_json(msg="Destination must be a full URL or path to a directory.")

        args.append(dest_string)

        # Detailed logging of the push operation
        if '/' in self.image_name:
            push_format_string = 'Pushed image {image_name}'
        else:
            push_format_string = 'Pushed image {image_name} to {dest}'
        self.results['actions'].append(push_format_string.format(image_name=self.image_name, dest=self.push_args['dest']))
        self.results['changed'] = True

        self.module.log("PODMAN-IMAGE-DEBUG: Pushing image {image_name} to {dest_string}".format(
            image_name=self.image_name, dest_string=dest_string))
        self.results['podman_actions'].append(" ".join([self.executable] + args))

        # Execute the push operation
        out, err = '', ''
        if not self.module.check_mode:
            rc, out, err = self._run(args, ignore_errors=True)
            if rc != 0:
                self.module.fail_json(msg="Failed to push image {image_name}".format(
                    image_name=self.image_name),
                    stdout=out, stderr=err,
                    actions=self.results['actions'],
                    podman_actions=self.results['podman_actions'])

        return self.inspect_image(self.image_name), out + err

    def remove_image(self, image_name=None):
        if image_name is None:
            image_name = self.image_name

        args = ['rmi', image_name]
        if self.force:
            args.append('--force')
        rc, out, err = self._run(args, ignore_errors=True)
        if rc != 0:
            self.module.fail_json(msg='Failed to remove image {image_name}. {err}'.format(image_name=image_name, err=err))
        return out

    def remove_image_id(self, image_id=None):
        if image_id is None:
            image_id = re.sub(':.*$', '', self.image_name)

        args = ['rmi', image_id]
        if self.force:
            args.append('--force')
        rc, out, err = self._run(args, ignore_errors=True)
        if rc != 0:
            self.module.fail_json(msg='Failed to remove image with id {image_id}. {err}'.format(
                image_id=image_id, err=err))
        return out


def parse_repository_tag(repo_name):
    parts = repo_name.rsplit('@', 1)
    if len(parts) == 2:
        return tuple(parts)
    parts = repo_name.rsplit(':', 1)
    if len(parts) == 2 and '/' not in parts[1]:
        return tuple(parts)
    return repo_name, None


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            arch=dict(type='str'),
            tag=dict(type='str', default='latest'),
            pull=dict(type='bool', default=True),
            pull_extra_args=dict(type='str'),
            push=dict(type='bool', default=False),
            path=dict(type='str'),
            force=dict(type='bool', default=False),
            state=dict(type='str', default='present', choices=['absent', 'present', 'build', 'quadlet']),
            validate_certs=dict(type='bool', aliases=['tlsverify', 'tls_verify']),
            executable=dict(type='str', default='podman'),
            auth_file=dict(type='path', aliases=['authfile']),
            username=dict(type='str'),
            password=dict(type='str', no_log=True),
            ca_cert_dir=dict(type='path'),
            quadlet_dir=dict(type='path', required=False),
            quadlet_filename=dict(type='str'),
            quadlet_options=dict(type='list', elements='str', required=False),
            build=dict(
                type='dict',
                aliases=['build_args', 'buildargs'],
                default={},
                options=dict(
                    annotation=dict(type='dict'),
                    force_rm=dict(type='bool', default=False),
                    file=dict(type='path'),
                    format=dict(
                        type='str',
                        choices=['oci', 'docker'],
                        default='oci'
                    ),
                    cache=dict(type='bool', default=True),
                    rm=dict(type='bool', default=True),
                    volume=dict(type='list', elements='str'),
                    extra_args=dict(type='str'),
                    target=dict(type='str'),
                ),
            ),
            push_args=dict(
                type='dict',
                default={},
                options=dict(
                    compress=dict(type='bool'),
                    format=dict(type='str', choices=['oci', 'v2s1', 'v2s2']),
                    remove_signatures=dict(type='bool'),
                    sign_by=dict(type='str'),
                    dest=dict(type='str', aliases=['destination'],),
                    extra_args=dict(type='str'),
                    transport=dict(
                        type='str',
                        choices=[
                            'dir',
                            'docker-archive',
                            'docker-daemon',
                            'oci-archive',
                            'ostree',
                            'docker'
                        ]
                    ),
                ),
            ),
        ),
        supports_check_mode=True,
        required_together=(
            ['username', 'password'],
        ),
        mutually_exclusive=(
            ['auth_file', 'username'],
            ['auth_file', 'password'],
        ),
    )

    results = dict(
        changed=False,
        actions=[],
        podman_actions=[],
        image={},
        stdout='',
    )

    PodmanImageManager(module, results)
    module.exit_json(**results)


if __name__ == '__main__':
    main()
