"""Response generator for humanized natural language responses based on Banking77 labels."""
import logging

logger = logging.getLogger(__name__)

# Comprehensive mapping of Banking77 labels to natural language responses
# Keys match Banking77 model output labels
# Values are dictionaries with "tr" and "en" natural language responses
RESPONSE_MAP = {
    "lost_or_stolen_card": {
        "tr": "Kart kayıp/çalıntı bildiriminiz alındı. Güvenliğiniz için kartınız geçici olarak kullanıma kapatılmıştır.",
        "en": "We have received your lost/stolen card report. Your card has been temporarily blocked for your security."
    },
    "change_pin": {
        "tr": "Şifre değiştirme işleminiz için sizi güvenlik adımına yönlendiriyorum.",
        "en": "I am redirecting you to the security step for your PIN change."
    },
    "balance_not_updated_after_cheque_or_cash_deposit": {
        "tr": "Çek veya nakit yatırma işleminizden sonra bakiye güncellemesi gecikmiş görünüyor. İşleminizi kontrol ediyorum.",
        "en": "Your balance update appears delayed after your cheque or cash deposit. I am checking your transaction."
    },
    "transfer_timing": {
        "tr": "Para transferi zamanlaması hakkında bilgi veriyorum. Transfer işlemleri genellikle iş günleri içinde tamamlanır.",
        "en": "I am providing information about transfer timing. Transfer transactions are usually completed within business days."
    },
    "fx_rate": {
        "tr": "Döviz kuru bilgilerinizi hazırlıyorum. Güncel kurlar için lütfen birkaç saniye bekleyiniz.",
        "en": "I am preparing your foreign exchange rate information. Please wait a few seconds for current rates."
    },
    "card_delivery_estimate": {
        "tr": "Kart teslimat tahmini için bilgilerinizi kontrol ediyorum. Yeni kartınız genellikle 5-7 iş günü içinde adresinize ulaşır.",
        "en": "I am checking your information for card delivery estimate. Your new card usually arrives at your address within 5-7 business days."
    },
    "card_swallowed": {
        "tr": "Kartınızın ATM tarafından alındığını görüyorum. Güvenlik nedeniyle kartınız bloke edilmiştir. Yeni kart talebi için sizi yönlendiriyorum.",
        "en": "I can see your card was retained by the ATM. Your card has been blocked for security reasons. I am redirecting you to request a new card."
    },
    "exchange_rate": {
        "tr": "Döviz kuru sorgulamanız işleniyor. Güncel kur bilgileri hazırlanıyor.",
        "en": "Your exchange rate inquiry is being processed. Current rate information is being prepared."
    },
    "pending_transfer": {
        "tr": "Bekleyen transfer işleminiz kontrol ediliyor. Transfer durumunuz kısa süre içinde paylaşılacak.",
        "en": "Your pending transfer is being checked. Your transfer status will be shared shortly."
    },
    "card_payment_fee_charged": {
        "tr": "Kart ödeme ücreti ile ilgili sorgulamanız inceleniyor. Ücret detaylarınız hazırlanıyor.",
        "en": "Your inquiry regarding card payment fee is being reviewed. Your fee details are being prepared."
    },
    "declined_card_payment": {
        "tr": "Reddedilen kart ödemesi ile ilgili durumunuz kontrol ediliyor. İşlem detaylarınız inceleniyor.",
        "en": "Your declined card payment status is being checked. Your transaction details are being reviewed."
    },
    "direct_debit_payment_not_recognised": {
        "tr": "Tanınmayan otomatik ödeme ile ilgili sorgulamanız kaydedildi. İşlem detaylarınız inceleniyor.",
        "en": "Your inquiry regarding unrecognized direct debit payment has been recorded. Your transaction details are being reviewed."
    },
    "disposable_card_limits": {
        "tr": "Tek kullanımlık kart limitleri hakkında bilgi veriyorum. Limit detaylarınız hazırlanıyor.",
        "en": "I am providing information about disposable card limits. Your limit details are being prepared."
    },
    "edit_personal_details": {
        "tr": "Kişisel bilgilerinizi güncelleme işlemi için sizi ilgili sayfaya yönlendiriyorum.",
        "en": "I am redirecting you to the relevant page to update your personal details."
    },
    "card_linking": {
        "tr": "Kart bağlama işleminiz için gerekli adımları uyguluyorum. İşlem devam ediyor.",
        "en": "I am applying the necessary steps for your card linking process. The transaction is in progress."
    },
    "country_support": {
        "tr": "Ülke desteği hakkında bilgi veriyorum. Desteklenen ülkeler listesi hazırlanıyor.",
        "en": "I am providing information about country support. The list of supported countries is being prepared."
    },
    "automatic_top_up": {
        "tr": "Otomatik yükleme ayarlarınız kontrol ediliyor. Yükleme tercihleriniz inceleniyor.",
        "en": "Your automatic top-up settings are being checked. Your top-up preferences are being reviewed."
    },
    "balance": {
        "tr": "Hesap bakiyenizi kontrol ediyorum. Bakiye bilgileriniz hazırlanıyor.",
        "en": "I am checking your account balance. Your balance information is being prepared."
    },
    "card_acceptance": {
        "tr": "Kart kabul durumunuz kontrol ediliyor. Kartınızın kabul edildiği yerler hakkında bilgi veriliyor.",
        "en": "Your card acceptance status is being checked. Information about where your card is accepted is being provided."
    },
    "card_arrival": {
        "tr": "Kartınızın teslimat durumu kontrol ediliyor. Teslimat bilgileriniz hazırlanıyor.",
        "en": "Your card delivery status is being checked. Your delivery information is being prepared."
    },
    "card_not_working": {
        "tr": "Çalışmayan kart sorununuz inceleniyor. Kartınızın teknik durumu kontrol ediliyor.",
        "en": "Your non-working card issue is being reviewed. Your card's technical status is being checked."
    },
    "contactless_not_working": {
        "tr": "Temassız özelliği çalışmayan kartınız için teknik destek sağlanıyor. Sorununuz inceleniyor.",
        "en": "Technical support is being provided for your card with non-working contactless feature. Your issue is being reviewed."
    },
    "get_physical_card": {
        "tr": "Fiziksel kart talebiniz alındı. Yeni kart basımı için işlem başlatılıyor.",
        "en": "Your physical card request has been received. The process for new card printing is being initiated."
    },
    "card_payment_wrong_exchange_rate": {
        "tr": "Yanlış döviz kuru ile yapılan kart ödemesi sorgulamanız inceleniyor. İşlem detaylarınız kontrol ediliyor.",
        "en": "Your inquiry regarding card payment with wrong exchange rate is being reviewed. Your transaction details are being checked."
    },
    "card_payment_not_recognised": {
        "tr": "Tanınmayan kart ödemesi ile ilgili sorgulamanız kaydedildi. İşlem detaylarınız inceleniyor.",
        "en": "Your inquiry regarding unrecognized card payment has been recorded. Your transaction details are being reviewed."
    },
    "verify_top_up": {
        "tr": "Yükleme doğrulama işleminiz kontrol ediliyor. Yükleme durumunuz inceleniyor.",
        "en": "Your top-up verification process is being checked. Your top-up status is being reviewed."
    },
    "top_up_by_bank_transfer_charge": {
        "tr": "Banka transferi ile yükleme ücreti sorgulamanız inceleniyor. Ücret detaylarınız hazırlanıyor.",
        "en": "Your inquiry regarding top-up charge by bank transfer is being reviewed. Your fee details are being prepared."
    },
    "top_up_by_card_charge": {
        "tr": "Kart ile yükleme ücreti sorgulamanız inceleniyor. Ücret detaylarınız hazırlanıyor.",
        "en": "Your inquiry regarding top-up charge by card is being reviewed. Your fee details are being prepared."
    },
    "top_up_failed": {
        "tr": "Başarısız yükleme işleminiz inceleniyor. Yükleme hatası tespit edildi, çözüm aranıyor.",
        "en": "Your failed top-up transaction is being reviewed. A top-up error has been detected and a solution is being sought."
    },
    "top_up_limits": {
        "tr": "Yükleme limitleri hakkında bilgi veriyorum. Limit detaylarınız hazırlanıyor.",
        "en": "I am providing information about top-up limits. Your limit details are being prepared."
    },
    "top_up_reverted": {
        "tr": "İptal edilen yükleme işleminiz kontrol ediliyor. İşlem durumunuz inceleniyor.",
        "en": "Your reverted top-up transaction is being checked. Your transaction status is being reviewed."
    },
    "pending_top_up": {
        "tr": "Bekleyen yükleme işleminiz kontrol ediliyor. Yükleme durumunuz kısa süre içinde paylaşılacak.",
        "en": "Your pending top-up transaction is being checked. Your top-up status will be shared shortly."
    },
    "passcode_forgotten": {
        "tr": "Unutulan şifre için sıfırlama işlemi başlatılıyor. Güvenlik adımları uygulanıyor.",
        "en": "A reset process for forgotten passcode is being initiated. Security steps are being applied."
    },
    "reverted_card_payment": {
        "tr": "İptal edilen kart ödemesi ile ilgili durumunuz kontrol ediliyor. İşlem detaylarınız inceleniyor.",
        "en": "Your reverted card payment status is being checked. Your transaction details are being reviewed."
    },
    "supported_cards_and_currencies": {
        "tr": "Desteklenen kartlar ve para birimleri hakkında bilgi veriyorum. Liste hazırlanıyor.",
        "en": "I am providing information about supported cards and currencies. The list is being prepared."
    },
    "unable_to_verify_identity": {
        "tr": "Kimlik doğrulama sorununuz inceleniyor. Doğrulama işlemi için alternatif yöntemler kontrol ediliyor.",
        "en": "Your identity verification issue is being reviewed. Alternative methods for verification are being checked."
    },
    "why_verify_identity": {
        "tr": "Kimlik doğrulama gerekliliği hakkında bilgi veriyorum. Güvenlik nedenleri açıklanıyor.",
        "en": "I am providing information about identity verification requirements. Security reasons are being explained."
    },
    "verify_my_identity": {
        "tr": "Kimlik doğrulama işleminiz başlatılıyor. Güvenlik adımları uygulanıyor.",
        "en": "Your identity verification process is being initiated. Security steps are being applied."
    },
    "age_verification": {
        "tr": "Yaş doğrulama işleminiz kontrol ediliyor. Doğrulama adımları uygulanıyor.",
        "en": "Your age verification process is being checked. Verification steps are being applied."
    },
    "apple_pay_or_google_pay": {
        "tr": "Apple Pay veya Google Pay ile ilgili sorgulamanız inceleniyor. Dijital cüzdan bilgileriniz hazırlanıyor.",
        "en": "Your inquiry regarding Apple Pay or Google Pay is being reviewed. Your digital wallet information is being prepared."
    },
    "beneficiary_not_allowed": {
        "tr": "İzin verilmeyen alıcı ile ilgili transfer durumunuz kontrol ediliyor. İşlem detaylarınız inceleniyor.",
        "en": "Your transfer status regarding non-allowed beneficiary is being checked. Your transaction details are being reviewed."
    },
    "cancel_transfer": {
        "tr": "Transfer iptal talebiniz alındı. İptal işlemi başlatılıyor.",
        "en": "Your transfer cancellation request has been received. The cancellation process is being initiated."
    },
    "card_about_to_expire": {
        "tr": "Süresi dolmak üzere olan kartınız için yeni kart talebi oluşturuluyor. Kart yenileme işlemi başlatılıyor.",
        "en": "A new card request is being created for your card that is about to expire. The card renewal process is being initiated."
    },
    "card_payment_fee_charged": {
        "tr": "Kart ödeme ücreti ile ilgili sorgulamanız inceleniyor. Ücret detaylarınız hazırlanıyor.",
        "en": "Your inquiry regarding card payment fee is being reviewed. Your fee details are being prepared."
    },
    "complaint": {
        "tr": "Şikayetiniz kaydedildi, incelenmeye alındı. En kısa sürede size dönüş yapılacaktır.",
        "en": "Your complaint has been recorded and is under review. You will be contacted as soon as possible."
    },
    "compromised_card": {
        "tr": "Güvenliği ihlal edilmiş kart bildiriminiz alındı. Kartınız acil olarak bloke edilmiştir.",
        "en": "Your compromised card report has been received. Your card has been immediately blocked."
    },
    "contactless_payment_after_limit": {
        "tr": "Limit sonrası temassız ödeme sorgulamanız inceleniyor. İşlem detaylarınız kontrol ediliyor.",
        "en": "Your inquiry regarding contactless payment after limit is being reviewed. Your transaction details are being checked."
    },
    "country_support": {
        "tr": "Ülke desteği hakkında bilgi veriyorum. Desteklenen ülkeler listesi hazırlanıyor.",
        "en": "I am providing information about country support. The list of supported countries is being prepared."
    },
    "declined_card_payment": {
        "tr": "Reddedilen kart ödemesi ile ilgili durumunuz kontrol ediliyor. İşlem detaylarınız inceleniyor.",
        "en": "Your declined card payment status is being checked. Your transaction details are being reviewed."
    },
    "direct_debit_inquiry": {
        "tr": "Otomatik ödeme sorgulamanız işleniyor. Otomatik ödeme bilgileriniz hazırlanıyor.",
        "en": "Your direct debit inquiry is being processed. Your direct debit information is being prepared."
    },
    "fiat_currency_support": {
        "tr": "Fiat para birimi desteği hakkında bilgi veriyorum. Desteklenen para birimleri listesi hazırlanıyor.",
        "en": "I am providing information about fiat currency support. The list of supported currencies is being prepared."
    },
    "get_disposable_virtual_card": {
        "tr": "Tek kullanımlık sanal kart talebiniz alındı. Kart oluşturma işlemi başlatılıyor.",
        "en": "Your disposable virtual card request has been received. The card creation process is being initiated."
    },
    "get_physical_card": {
        "tr": "Fiziksel kart talebiniz alındı. Yeni kart basımı için işlem başlatılıyor.",
        "en": "Your physical card request has been received. The process for new card printing is being initiated."
    },
    "increase_card_limit": {
        "tr": "Kart limiti artırma talebiniz alındı. Limit artırma işlemi için onay sürecine geçiliyor.",
        "en": "Your card limit increase request has been received. The approval process for limit increase is being initiated."
    },
    "increase_transaction_limit": {
        "tr": "İşlem limiti artırma talebiniz alındı. Limit artırma işlemi için onay sürecine geçiliyor.",
        "en": "Your transaction limit increase request has been received. The approval process for limit increase is being initiated."
    },
    "pending_card_payment": {
        "tr": "Bekleyen kart ödemesi kontrol ediliyor. Ödeme durumunuz kısa süre içinde paylaşılacak.",
        "en": "Your pending card payment is being checked. Your payment status will be shared shortly."
    },
    "pending_transfer": {
        "tr": "Bekleyen transfer işleminiz kontrol ediliyor. Transfer durumunuz kısa süre içinde paylaşılacak.",
        "en": "Your pending transfer is being checked. Your transfer status will be shared shortly."
    },
    "pending_top_up": {
        "tr": "Bekleyen yükleme işleminiz kontrol ediliyor. Yükleme durumunuz kısa süre içinde paylaşılacak.",
        "en": "Your pending top-up transaction is being checked. Your top-up status will be shared shortly."
    },
    "pin_blocked": {
        "tr": "PIN bloke durumunuz kontrol ediliyor. PIN sıfırlama işlemi için sizi güvenlik adımına yönlendiriyorum.",
        "en": "Your PIN blocked status is being checked. I am redirecting you to the security step for PIN reset."
    },
    "receipt": {
        "tr": "Makbuz talebiniz işleniyor. İşlem makbuzunuz hazırlanıyor.",
        "en": "Your receipt request is being processed. Your transaction receipt is being prepared."
    },
    "refund_not_showing_up": {
        "tr": "Görünmeyen iade işleminiz kontrol ediliyor. İade durumunuz inceleniyor.",
        "en": "Your refund that is not showing up is being checked. Your refund status is being reviewed."
    },
    "request_refund": {
        "tr": "İade talebiniz alındı. İade işlemi için onay sürecine geçiliyor.",
        "en": "Your refund request has been received. The approval process for refund is being initiated."
    },
    "reverted_card_payment": {
        "tr": "İptal edilen kart ödemesi ile ilgili durumunuz kontrol ediliyor. İşlem detaylarınız inceleniyor.",
        "en": "Your reverted card payment status is being checked. Your transaction details are being reviewed."
    },
    "reverted_transfer": {
        "tr": "İptal edilen transfer işleminiz kontrol ediliyor. Transfer durumunuz inceleniyor.",
        "en": "Your reverted transfer is being checked. Your transfer status is being reviewed."
    },
    "terminate_account": {
        "tr": "Hesap kapatma talebiniz alındı. Hesap kapatma işlemi için onay sürecine geçiliyor.",
        "en": "Your account termination request has been received. The approval process for account closure is being initiated."
    },
    "transfer_into_account": {
        "tr": "Hesaba transfer işleminiz kontrol ediliyor. Transfer durumunuz inceleniyor.",
        "en": "Your transfer into account is being checked. Your transfer status is being reviewed."
    },
    "transfer_not_received_by_recipient": {
        "tr": "Alıcı tarafından alınmayan transfer işleminiz kontrol ediliyor. Transfer durumunuz inceleniyor.",
        "en": "Your transfer not received by recipient is being checked. Your transfer status is being reviewed."
    },
    "unable_to_verify_identity": {
        "tr": "Kimlik doğrulama sorununuz inceleniyor. Doğrulama işlemi için alternatif yöntemler kontrol ediliyor.",
        "en": "Your identity verification issue is being reviewed. Alternative methods for verification are being checked."
    },
    "verify_my_identity": {
        "tr": "Kimlik doğrulama işleminiz başlatılıyor. Güvenlik adımları uygulanıyor.",
        "en": "Your identity verification process is being initiated. Security steps are being applied."
    },
    "verify_top_up": {
        "tr": "Yükleme doğrulama işleminiz kontrol ediliyor. Yükleme durumunuz inceleniyor.",
        "en": "Your top-up verification process is being checked. Your top-up status is being reviewed."
    },
    "virtual_card_not_working": {
        "tr": "Çalışmayan sanal kart sorununuz inceleniyor. Kartınızın teknik durumu kontrol ediliyor.",
        "en": "Your non-working virtual card issue is being reviewed. Your card's technical status is being checked."
    },
    "visa_or_mastercard": {
        "tr": "Visa veya Mastercard desteği hakkında bilgi veriyorum. Kart türü bilgileriniz hazırlanıyor.",
        "en": "I am providing information about Visa or Mastercard support. Your card type information is being prepared."
    },
    "why_verify_identity": {
        "tr": "Kimlik doğrulama gerekliliği hakkında bilgi veriyorum. Güvenlik nedenleri açıklanıyor.",
        "en": "I am providing information about identity verification requirements. Security reasons are being explained."
    }
}

# Generic fallback responses for unknown intents
GENERIC_RESPONSES = {
    "tr": [
        "Talebiniz alındı, inceleniyor. En kısa sürede size yardımcı olunacaktır.",
        "Sorunuz kaydedildi, ilgili birime yönlendiriliyorsunuz. Kısa süre içinde yanıt verilecektir.",
        "Talebiniz işleme alındı, bilgilendirme yapılacaktır.",
        "Sorunuz değerlendiriliyor, en uygun çözüm hazırlanıyor.",
        "Talebiniz kaydedildi, en kısa sürede size dönüş yapılacaktır."
    ],
    "en": [
        "Your request has been received and is under review. We will assist you as soon as possible.",
        "Your inquiry has been recorded and you are being directed to the relevant department. A response will be provided shortly.",
        "Your request has been processed and you will be informed.",
        "Your inquiry is being evaluated and the most appropriate solution is being prepared.",
        "Your request has been recorded and you will be contacted as soon as possible."
    ]
}


def generate_response(intent: str, language: str = "tr") -> str:
    """
    Generate humanized natural language response based on Banking77 intent label.
    
    This function maps raw Banking77 model labels (e.g., "lost_or_stolen_card") 
    to natural, user-friendly responses in the requested language.
    
    Args:
        intent: The predicted intent/classification label from Banking77 model
        language: Language code ("tr" for Turkish, "en" for English)
        
    Returns:
        A natural language response sentence for the given intent and language
    """
    # Normalize intent for matching (lowercase, handle variations)
    normalized_intent = intent.lower().strip().replace(" ", "_")
    
    # Try exact match first
    if normalized_intent in RESPONSE_MAP:
        response_dict = RESPONSE_MAP[normalized_intent]
        response = response_dict.get(language, response_dict.get("en", ""))
        if response:
            logger.debug(f"Found exact match for intent '{intent}' in language '{language}'")
            return response
    
    # Try matching with underscores/slashes variations
    intent_variations = [
        normalized_intent,
        normalized_intent.replace("_", " "),
        normalized_intent.replace("_", "-"),
        intent.lower().strip()
    ]
    
    for variation in intent_variations:
        if variation in RESPONSE_MAP:
            response_dict = RESPONSE_MAP[variation]
            response = response_dict.get(language, response_dict.get("en", ""))
            if response:
                logger.debug(f"Found match for intent '{intent}' via variation '{variation}'")
                return response
    
    # Try partial matching (check if any key contains the intent or vice versa)
    for key in RESPONSE_MAP.keys():
        key_normalized = key.lower().replace("_", "").replace("-", "").replace(" ", "")
        intent_normalized = normalized_intent.replace("_", "").replace("-", "").replace(" ", "")
        
        # Check if intent is contained in key or key is contained in intent
        if key_normalized in intent_normalized or intent_normalized in key_normalized:
            response_dict = RESPONSE_MAP[key]
            response = response_dict.get(language, response_dict.get("en", ""))
            if response:
                logger.debug(f"Matched intent '{intent}' to key '{key}' via partial match")
                return response
    
    # Fallback to generic response if no match found
    logger.warning(f"Unknown intent '{intent}', using generic response for language '{language}'")
    import random
    fallback_responses = GENERIC_RESPONSES.get(language, GENERIC_RESPONSES["en"])
    return random.choice(fallback_responses)
