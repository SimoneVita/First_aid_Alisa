import requests
import navidata


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    
    TOKEN = 'ENTER TELEGRAM TOKEN'
    CHAT_ID = 'ENTER CHAT ID'

    keys = list()
    tg_info = []
    status = 'null'

    def send_message(answer, status):
        """Отправка сообщения в Telegram чат."""
        if status == 'valid':
            message = f'Был сделан запрос "{answer[0]}", информация передана пользователю из файла {answer[1]}.'
        elif status == 'invalid':
            message = f'Был сделан запрос "{answer[0]}", который отсутствует в БД.'
        else:
            message = f'Произошла неизвестная ошибка - статус неопределен. Был сделан запрос "{answer[0]}".'
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        requests.get(url).json()
        return message
    

    if 'request' in event and \
            'original_utterance' in event['request'] \
            and len(event['request']['original_utterance']) > 0:
        text = event['request']['original_utterance']
        tokens = event['request']['nlu']['tokens']
        for token in tokens:
            if token not in navidata.non_used_words:
                keys.append(token)

    if event['session']['new'] == True:
        text = 'Привет! Я бот Первой помощи, назовите коротко и четко, с чем именно мы имеем дело! Например, "инфаркт". Также у меня всегда можно спросить "Что ты умеешь?" и "Помощь".'
    elif text.lower() in navidata.diseases:
        tg_info.append(text)
        tg_info.append(navidata.diseases[text.lower()])
        answer = open(navidata.diseases[text.lower()], 'r')
        status = 'valid'
        text = answer.read()
    else:  
        for word in keys:
            if word.lower() in navidata.diseases:
                tg_info.append(text)
                tg_info.append(navidata.diseases[word.lower()])
                answer = open(navidata.diseases[word.lower()], 'r')
                status = 'valid'
                text = answer.read()
                break
        if status != 'valid':
            tg_info.append(text)
            status = 'invalid'
            text = f'Я не знаю, что делать в этой ситуации, но я предупрежу админа и скоро информацию добавят.'
    
    if status != 'null':
        send_message(tg_info, status)

    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            # Respond with the original request or welcome the user if this is the beginning of the dialog and the request has not yet been made.
            'text': text,
            # Don't finish the session after this response.
            'end_session': 'false'
        },
    }
