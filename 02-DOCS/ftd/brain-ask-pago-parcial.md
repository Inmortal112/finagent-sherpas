---
created: 2026-11-16
status: done
branch: fix/brain-ask-partial-paydown
---
# `/ask` ya no dice que pagar parte de la tarjeta la salda

## Intención
A veces `/ask` decía «That clears your costliest debt» del paso de los Weah, que paga $6,800 de una tarjeta de
$18,000. No es una cifra, así que `guard` no lo veía; la regla en las instrucciones lo arreglaba solo a medias
(1 de 4 respuestas seguía mal, ver `verificacion-web-completa.md`).

## Alcance
- Entra: un hecho nuevo en el paso (el saldo de la tarjeta hoy) y una comprobación de `guard` en ese paso.
- No entra: cambiar el contrato, los textos guardados en `narrations/` ni la página. Solo afecta a un paso de
  una familia (es el único que paga parte de una deuda); otros pasos parciales (seguros) quedan como estaban.

## Checklist
- [x] `house.part_paid_card_balance`: si el paso «Pay down revolving card» paga menos que el saldo de la tarjeta,
      devuelve el saldo (los dos datos son de Sherpas; no se calcula «lo que queda»). → test
- [x] `brain`: ese paso lleva el hecho `move_N_card_balance` y `visual.data.pays_part_of_debt`. → test
- [x] `guard.claims_debt_cleared` + `narrator.check`: en ese paso se rechaza «clears / pays off / wipes out…»
      salvo que la frase diga «not», «the rest», «what is left». «Clear the gate» (texto de Sherpas) y «pay $6,800
      off the card» pasan. Con el rechazo, el modelo tiene un reintento y después suena la narración aprobada. → test
- [x] Los textos guardados de las cuatro familias en los dos modos siguen pasando. → test
- [x] Probado con el modelo real.

## Evidencia
- `./check.sh` → `166 passed`, `OK -> out/index.html`.
- Modelo real (`deepseek-flash`, 16 nov), 6 preguntas a los Weah («is the credit card gone?», «does it clear our
  most expensive debt?», «how do we get rid of the card?»…): 6 de 6 dicen que paga parte y que el resto se sigue
  debiendo. Ejemplo: «Not yet. That step pays $6,800 toward the 18% card… the card balance is $18,000 and the rest
  is still owed.» Coste de las seis: $0.009 (gasto del equipo: $0.62 → $0.63 de $50).

## Siguiente
Regenerar `out/` (`finagent.run --all`) antes del ensayo, para que la página lleve el hecho nuevo.
