const SHEET_NAME = '勤怠ログ';

function doPost(e) {
  try {
    const payload = parsePayload_(e);
    validatePayload_(payload);
    const now = new Date();

    const jst = Utilities.formatDate(now, 'Asia/Tokyo', 'yyyy-MM-dd');
    const jstTime = Utilities.formatDate(now, 'Asia/Tokyo', 'HH:mm:ss');

    const isoTime = new Date(payload.isoTime);
    const recordDate = Utilities.formatDate(isoTime, 'Asia/Tokyo', 'yyyy-MM-dd');
    const recordTime = Utilities.formatDate(isoTime, 'Asia/Tokyo', 'HH:mm:ss');

    const row = [
      recordDate,
      recordTime,
      payload.type,
      payload.userName,
      payload.userId,
      payload.messageId,
      payload.channelId,
      payload.content,
      `${jst} ${jstTime}`,
    ];

    const sheet = getSheet_();
    sheet.appendRow(row);

    return jsonResponse_({ ok: true });
  } catch (err) {
    return jsonResponse_({ ok: false, error: String(err) }, 400);
  }
}

function parsePayload_(e) {
  if (!e || !e.postData || !e.postData.contents) {
    throw new Error('Missing body');
  }
  return JSON.parse(e.postData.contents);
}

function validatePayload_(payload) {
  const secret = getSecret_();
  if (!payload || payload.secret !== secret) {
    throw new Error('Unauthorized');
  }

  const allowedTypes = ['clock_in', 'clock_out'];
  if (!allowedTypes.includes(payload.type)) {
    throw new Error('Invalid type');
  }

  const requiredFields = [
    'isoTime',
    'userId',
    'userName',
    'messageId',
    'channelId',
    'content',
  ];

  for (const field of requiredFields) {
    if (!payload[field]) {
      throw new Error(`Missing field: ${field}`);
    }
  }
}

function getSheet_() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) {
    throw new Error(`Sheet not found: ${SHEET_NAME}`);
  }
  return sheet;
}

function getSecret_() {
  const secret = PropertiesService.getScriptProperties().getProperty('SHARED_SECRET');
  if (!secret) {
    throw new Error('Script property SHARED_SECRET is not set');
  }
  return secret;
}

function jsonResponse_(obj, statusCode) {
  const output = ContentService.createTextOutput(JSON.stringify(obj));
  output.setMimeType(ContentService.MimeType.JSON);

  if (statusCode && output.setResponseCode) {
    output.setResponseCode(statusCode);
  }

  return output;
}
