#!/bin/sh
# Genera la config S3 de SeaweedFS con las credenciales del entorno y arranca el
# servidor. Se hace al iniciar el contenedor (no al construir la imagen) para que
# STORAGE_ACCESS_KEY y STORAGE_SECRET_KEY nunca queden guardadas en una capa.
set -eu

mkdir -p /etc/seaweedfs
cat > /etc/seaweedfs/s3.json <<EOF
{
  "identities": [
    {
      "name": "api",
      "credentials": [
        { "accessKey": "${STORAGE_ACCESS_KEY}", "secretKey": "${STORAGE_SECRET_KEY}" }
      ],
      "actions": ["Admin", "Read", "Write", "List", "Tagging"]
    }
  ]
}
EOF

exec weed server -dir=/data -s3 -s3.config=/etc/seaweedfs/s3.json -master.volumeSizeLimitMB=1024
