import json
import os
from os.path import getmtime
from zipfile import ZipFile

REPO_URL = 'https//ffxivita.github.io/DalamudPlugins/plugins/{plugin_name}/latest.zip'

DEFAULTS = {
    'IsHide': False,
    'IsTestingExclusive': False,
    'ApplicableVersion': 'any'
}

DUPLICATES = {
    'DownloadLinkInstall': [
        'DownloadLinkTesting',
        'DownloadLinkUpdate'
    ]
}

TRIMMED_KEYS = [
    'Author',
    'Name',
    'Description',
    'InternalName',
    'AssemblyVersion',
    'RepoUrl',
    'ApplicableVersion',
    'Tags',
    'DalamudApiLevel',
    'IsTestingExclusive',
    'IconUrl',
    'ImageUrls'
]


def main():
    # estrai i manifest da dentro i file zip
    master = extract_manifests()

    # trim i manifest
    master = [trim_manifest(manifest) for manifest in master]

    # converti la lista dei manifest nella master list
    add_extra_fields(master)

    # Aggiorna il field LastUpdated dentro master
    last_updated(master)

    # Scrivi il file master
    write_master(master)


def extract_manifests():
    manifests = []

    for dirpath, dirnames, filenames in os.walk('./plugins'):
        if len(filenames) == 0 or 'latest.zip' not in filenames:
            continue
        plugin_name = dirpath.split('/')[-1]
        latest_zip = f'{dirpath}/latest.zip'
        with ZipFile(latest_zip) as z:
            manifest = json.loads(z.read(f'{plugin_name}.json').decode('utf-8'))
            manifests.append(manifest)
    return manifests


def add_extra_fields(manifests):
    for manifest in manifests:
        # genera il link di download dalla variabile AssemblyName
        manifest['DownloadLinkInstall'] = REPO_URL.format(plugin_name=manifest['InternalName'])
        # aggiungi le variabili di default se non presenti
        for k, v in DEFAULTS.items():
            manifest[k] = v

        # duplica le chiavi come specificato in DUPLICATES
        for source, keys in DUPLICATES.items():
            for k in manifest:
                if k not in manifest:
                    manifest[k] = manifest[source]
        manifest['DownloadCount'] = 0


def write_master(master):
    # scrivi un bel file json e formattalo
    with open('pluginmaster.json', 'w') as f:
        json.dump(master, f, indent=4)


def trim_manifest(plugin):
    return {k: plugin[k] for k in TRIMMED_KEYS if k in plugin}


def last_updated(master):
    for plugin in master:
        latest = f'plugins/{plugin["InternalName"]}/latest.zip'
        modified = int(getmtime(latest))

        if 'LastUpdated' not in plugin or modified != int(plugin['LastUpdated']):
            plugin['LastUpdated'] = str(modified)


if __name__ == '__main__':
    main()
