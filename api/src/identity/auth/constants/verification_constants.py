EMAIL_BODY = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Código de verificación</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f7fa;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
  <table role="presentation" style="width:100%;border-collapse:collapse;">
    <tr>
      <td align="center" style="padding:40px 0;">
        <table role="presentation" style="width:100%;max-width:600px;border-collapse:collapse;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,.1);">
          <tr>
            <td style="background:linear-gradient(135deg,#006FEE 0%,#0052CC 100%);padding:40px 30px;text-align:center;">
              <h1 style="margin:0;color:#fff;font-size:28px;font-weight:600;">Verificación de cuenta</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:40px 30px;">
              <p style="margin:0 0 20px;color:#333;font-size:16px;">Estimado/a <strong>{name}</strong>,</p>
              <p style="margin:0 0 30px;color:#666;font-size:15px;">Hemos recibido una solicitud de verificación para su cuenta. Utilice el siguiente código para completar el proceso:</p>
              <div style="background:linear-gradient(135deg,#006FEE 0%,#0052CC 100%);border-radius:12px;padding:30px;text-align:center;margin:30px 0;">
                <p style="margin:0 0 10px;color:rgba(255,255,255,.9);font-size:14px;text-transform:uppercase;letter-spacing:1px;">Código de verificación</p>
                <p style="margin:0;color:#fff;font-size:40px;font-weight:700;letter-spacing:10px;font-family:'Courier New',monospace;">{code}</p>
              </div>
              <div style="background:#fff3cd;border-left:4px solid #ffc107;padding:15px 20px;border-radius:4px;">
                <p style="margin:0;color:#856404;font-size:14px;"><strong>Este código tiene una validez de 5 minutos.</strong> Por seguridad, no lo comparta con nadie.</p>
              </div>
              <p style="margin:20px 0 0;color:#666;font-size:14px;">Si usted no realizó esta solicitud, puede ignorar este mensaje. Su cuenta permanece segura.</p>
            </td>
          </tr>
          <tr>
            <td style="background:#f8f9fa;padding:20px 30px;text-align:center;border-top:1px solid #e9ecef;">
              <p style="margin:0;color:#aaa;font-size:12px;">Este es un mensaje automático. Por favor no respondas.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


SMS_TEMPLATE = "Su código de verificación es {code}. Válido por 5 minutos. Por seguridad, no lo comparta con nadie."
