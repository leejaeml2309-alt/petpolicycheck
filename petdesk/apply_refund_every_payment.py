"""Gumroad's refund policy is set per product and covers every payment, so the 14-day guarantee now
applies to each subscription payment (first payment and renewals). Patches the legal pages
(site/ and static/, kept identical) and the copy sources. Idempotent. Not part of build.py."""
import pathlib
R = pathlib.Path(__file__).resolve().parent.parent
PRE = {"en": "", "fr": "fr/", "es": "es/", "de": "de/", "it": "it/", "ja": "ja/"}
REFUND = {
"en": [("If the first charge is taken after the trial, the 14-day refund guarantee below applies from the date of that charge.",
        "The 14-day refund guarantee below applies to that first charge and to every renewal charge after it."),
       ("If you are not satisfied with your initial B2B Pet Desk subscription purchase (monthly or annual), you may request a <strong>full refund within 14 calendar days</strong> of the purchase date.",
        "If you are not satisfied, you may request a <strong>full refund within 14 calendar days</strong> of any B2B Pet Desk subscription payment (monthly or annual, first payment or renewal), counted from the date of that payment."),
       ("it starts on the date of your first payment (for Starter, the day the free month ends), not on the trial start date, and taking the trial does not shorten it.",
        "it counts from the date of each payment (for Starter, the first payment is taken the day the free month ends), not from the trial start date, and taking the trial does not shorten it.")],
"fr": [("Si le premier prélèvement a lieu après l’essai, la garantie de remboursement de 14 jours ci-dessous s’applique à partir de la date de ce prélèvement.",
        "La garantie de remboursement de 14 jours ci-dessous s’applique à ce premier prélèvement et à chaque prélèvement de renouvellement qui suit."),
       ("Si vous n’êtes pas satisfait de votre premier achat d’abonnement B2B Pet Desk (mensuel ou annuel), vous pouvez demander un <strong>remboursement intégral dans un délai de 14 jours calendaires</strong> à compter de la date d’achat.",
        "Si vous n’êtes pas satisfait, vous pouvez demander un <strong>remboursement intégral dans un délai de 14 jours calendaires</strong> pour tout paiement d’abonnement B2B Pet Desk (mensuel ou annuel, premier paiement ou renouvellement), à compter de la date de ce paiement."),
       ("elle commence à la date de votre premier paiement (pour Starter, le jour où le mois gratuit se termine), et non à la date de début de l’essai, et l’essai ne la raccourcit pas.",
        "elle court à partir de la date de chaque paiement (pour Starter, le premier paiement a lieu le jour où le mois gratuit se termine), et non de la date de début de l’essai, et l’essai ne la raccourcit pas.")],
"es": [("Si el primer cargo se realiza después de la prueba, la garantía de reembolso de 14 días que figura abajo se aplica desde la fecha de ese cargo.",
        "La garantía de reembolso de 14 días que figura abajo se aplica a ese primer cargo y a cada cargo de renovación posterior."),
       ("Si no está satisfecho con su compra inicial de suscripción a B2B Pet Desk (mensual o anual), puede solicitar un <strong>reembolso completo dentro de los 14 días naturales</strong> siguientes a la fecha de compra.",
        "Si no está satisfecho, puede solicitar un <strong>reembolso completo dentro de los 14 días naturales</strong> siguientes a cualquier pago de suscripción a B2B Pet Desk (mensual o anual, primer pago o renovación), contados desde la fecha de ese pago."),
       ("empieza en la fecha de su primer pago (en Starter, el día en que termina el mes gratuito), no en la fecha de inicio de la prueba, y la prueba no lo acorta.",
        "se cuenta desde la fecha de cada pago (en Starter, el primer pago se realiza el día en que termina el mes gratuito), no desde la fecha de inicio de la prueba, y la prueba no lo acorta.")],
"de": [("Erfolgt die erste Abbuchung nach der Testphase, gilt die 14-tägige Rückerstattungsgarantie unten ab dem Datum dieser Abbuchung.",
        "Die 14-tägige Rückerstattungsgarantie unten gilt für diese erste Abbuchung und für jede spätere Verlängerungsabbuchung."),
       ("Wenn Sie mit Ihrem ersten Kauf eines Abonnements von B2B Pet Desk (monatlich oder jährlich) nicht zufrieden sind, können Sie eine <strong>vollständige Erstattung innerhalb von 14 Kalendertagen</strong> ab dem Kaufdatum verlangen.",
        "Wenn Sie nicht zufrieden sind, können Sie für jede Abonnementzahlung von B2B Pet Desk (monatlich oder jährlich, erste Zahlung oder Verlängerung) eine <strong>vollständige Erstattung innerhalb von 14 Kalendertagen</strong> ab dem Datum dieser Zahlung verlangen."),
       ("Sie beginnt am Tag Ihrer ersten Zahlung (bei Starter an dem Tag, an dem der Gratismonat endet), nicht am Beginn der Testphase, und die Testphase verkürzt sie nicht.",
        "Sie läuft ab dem Datum jeder Zahlung (bei Starter erfolgt die erste Zahlung an dem Tag, an dem der Gratismonat endet), nicht ab dem Beginn der Testphase, und die Testphase verkürzt sie nicht.")],
"it": [("Se il primo addebito avviene dopo la prova, la garanzia di rimborso di 14 giorni indicata sotto si applica dalla data di tale addebito.",
        "La garanzia di rimborso di 14 giorni indicata sotto si applica a questo primo addebito e a ogni successivo addebito di rinnovo."),
       ("Se non è soddisfatto del Suo acquisto iniziale dell'abbonamento B2B Pet Desk (mensile o annuale), può richiedere un <strong>rimborso integrale entro 14 giorni di calendario</strong> dalla data di acquisto.",
        "Se non è soddisfatto, può richiedere un <strong>rimborso integrale entro 14 giorni di calendario</strong> per qualsiasi pagamento dell'abbonamento B2B Pet Desk (mensile o annuale, primo pagamento o rinnovo), a decorrere dalla data di tale pagamento."),
       ("decorre dalla data del Suo primo pagamento (per Starter, il giorno in cui termina il mese gratuito), non dalla data di inizio della prova, e la prova non lo riduce.",
        "decorre dalla data di ciascun pagamento (per Starter, il primo pagamento avviene il giorno in cui termina il mese gratuito), non dalla data di inizio della prova, e la prova non lo riduce.")],
"ja": [("試用後に最初の請求が行われた場合は、その請求日から下記の14日間返金保証が適用されます。",
        "下記の14日間返金保証は、この最初の請求と、その後の各更新請求に適用されます。"),
       ("B2B Pet Deskサブスクリプションの初回購入（月額または年額）にご満足いただけない場合は、購入日から<strong>14暦日以内に全額返金</strong>を請求できます。",
        "ご満足いただけない場合は、B2B Pet Deskサブスクリプションの各お支払い（月額または年額、初回または更新）について、そのお支払い日から<strong>14暦日以内に全額返金</strong>を請求できます。"),
       ("試用開始日ではなく、最初のお支払い日（Starterの場合は無料の1か月が終わる日）から始まり、試用によって短縮されることはありません。",
        "試用開始日ではなく、各お支払い日（Starterの初回のお支払いは無料の1か月が終わる日）から数え、試用によって短縮されることはありません。")],
}
TERMS = {
"en": [("The guarantee applies to an initial paid subscription purchase, monthly or annual. Its 14-calendar-day period starts on the date of your first payment (for Starter, the day the free month ends and Gumroad takes the first charge), not on the trial start date.",
        "The guarantee applies to every subscription payment, monthly or annual, including renewals. Its 14-calendar-day period starts on the date of each payment (for Starter, the first payment is taken the day the free month ends), not on the trial start date."),
       ("</strong> on initial purchases", "</strong> on every subscription payment")],
"fr": [("La garantie s’applique au premier achat d’abonnement payant, mensuel ou annuel. Sa période de 14 jours calendaires commence à la date de votre premier paiement (pour Starter, le jour où le mois gratuit se termine et où Gumroad effectue le premier prélèvement), et non à la date de début de l’essai.",
        "La garantie s’applique à chaque paiement d’abonnement, mensuel ou annuel, renouvellements compris. Sa période de 14 jours calendaires commence à la date de chaque paiement (pour Starter, le premier paiement a lieu le jour où le mois gratuit se termine), et non à la date de début de l’essai."),
       ("sur les premiers achats", "sur chaque paiement d’abonnement")],
"es": [("La garantía se aplica a una compra inicial de suscripción de pago, mensual o anual. Su plazo de 14 días naturales empieza en la fecha de su primer pago (en Starter, el día en que termina el mes gratuito y Gumroad realiza el primer cargo), no en la fecha de inicio de la prueba.",
        "La garantía se aplica a cada pago de suscripción, mensual o anual, incluidas las renovaciones. Su plazo de 14 días naturales empieza en la fecha de cada pago (en Starter, el primer pago se realiza el día en que termina el mes gratuito), no en la fecha de inicio de la prueba."),
       ("</strong> en las compras iniciales", "</strong> en cada pago de suscripción")],
"de": [("Die Garantie gilt für den ersten Kauf eines kostenpflichtigen Abonnements, monatlich oder jährlich. Ihre Frist von 14 Kalendertagen beginnt am Tag Ihrer ersten Zahlung (bei Starter an dem Tag, an dem der Gratismonat endet und Gumroad die erste Abbuchung vornimmt), nicht am Beginn der Testphase.",
        "Die Garantie gilt für jede Abonnementzahlung, monatlich oder jährlich, einschließlich Verlängerungen. Ihre Frist von 14 Kalendertagen beginnt am Tag der jeweiligen Zahlung (bei Starter erfolgt die erste Zahlung an dem Tag, an dem der Gratismonat endet), nicht am Beginn der Testphase."),
       ("</strong> für erste Käufe", "</strong> für jede Abonnementzahlung")],
"it": [("La garanzia si applica al primo acquisto di un abbonamento a pagamento, mensile o annuale. Il periodo di 14 giorni di calendario decorre dalla data del Suo primo pagamento (per Starter, il giorno in cui termina il mese gratuito e Gumroad effettua il primo addebito), non dalla data di inizio della prova.",
        "La garanzia si applica a ogni pagamento dell'abbonamento, mensile o annuale, compresi i rinnovi. Il periodo di 14 giorni di calendario decorre dalla data di ciascun pagamento (per Starter, il primo pagamento avviene il giorno in cui termina il mese gratuito), non dalla data di inizio della prova."),
       ("</strong> sugli acquisti iniziali", "</strong> su ogni pagamento dell'abbonamento")],
"ja": [("保証は、月額または年額の有料サブスクリプションの初回購入に適用されます。14暦日の期間は、試用開始日ではなく、最初のお支払い日（Starterの場合は、無料の1か月が終わりGumroadが最初の請求を行う日）から始まります。",
        "保証は、更新を含む月額または年額のサブスクリプションの各お支払いに適用されます。14暦日の期間は、試用開始日ではなく、各お支払い日（Starterの初回のお支払いは無料の1か月が終わる日）から始まります。"),
       ("初回購入に対する明確な", "サブスクリプションの各お支払いに対する明確な")],
}
def patch(path, pairs):
    t = path.read_text(); n = 0
    for a, b in pairs:
        if b in t: continue
        assert t.count(a) == 1, (path, a[:60], t.count(a)); t = t.replace(a, b); n += 1
    path.write_text(t); return n
if __name__ == "__main__":
    for l, pre in PRE.items():
        for doc, table in (("refund-policy.html", REFUND), ("terms.html", TERMS)):
            for root in ("site", "static"):
                patch(R / root / pre / doc, table[l])
    # keep the copy source in step (legal text authored in copy_legal.py)
    src = R / "petdesk/copy_legal.py"; s = src.read_text()
    for l in PRE:
        for a, b in REFUND[l] + TERMS[l]:
            a2 = a.replace("<strong>", "").replace("</strong>", "")
            if a in s: s = s.replace(a, b)
    src.write_text(s)
    print("ok")
