import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

df1 = pd.read_csv("moji_mars_podaci/mars_lokacije.csv", sep=";", decimal=",")
df2 = pd.read_csv("moji_mars_podaci/mars_uzorci.csv", sep=";", decimal=",")

df = pd.merge(df1, df2, on="ID_Uzorka")

uvjet = (
    (df["Temp_Tla_C"] >= -100) & (df["Temp_Tla_C"] <= 40) &
    (df["pH_Vrijednost"] >= 0) & (df["pH_Vrijednost"] <= 14) &
    (df["H2O_Postotak"] >= 0) & (df["H2O_Postotak"] <= 100)
)

df_cisto = df[uvjet]
df_anomalije = df[~uvjet]

df_cisto.to_csv("cisti_podaci.csv", index=False)
df_anomalije.to_csv("anomalije.csv", index=False)

sns.set_theme(style="whitegrid")

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_cisto, x="Temp_Tla_C", y="H2O_Postotak", hue="Metan_Senzor")
plt.savefig("1_temperatura_voda.png", dpi=200)
plt.close()

plt.figure(figsize=(10, 6))
plt.scatter(df_cisto["GPS_LONG"], df_cisto["GPS_LAT"], c=df_cisto["Dubina_Busenja_cm"], cmap="viridis", s=20)
plt.colorbar(label="Dubina bušenja")
plt.savefig("2_karta_dubine.png", dpi=200)
plt.close()

plt.figure(figsize=(10, 6))
df_poz = df_cisto[df_cisto["Metan_Senzor"] == "Pozitivno"]
df_neg = df_cisto[df_cisto["Metan_Senzor"] != "Pozitivno"]
plt.scatter(df_neg["GPS_LONG"], df_neg["GPS_LAT"], color="blue", s=15)
plt.scatter(df_poz["GPS_LONG"], df_poz["GPS_LAT"], color="red", s=15)
plt.savefig("3_metan.png", dpi=200)
plt.close()

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_cisto, x="GPS_LONG", y="GPS_LAT", hue="H2O_Postotak", palette="Blues", legend=False, alpha=0.3)
df_kandidati = df_cisto[(df_cisto["Metan_Senzor"] == "Pozitivno") & (df_cisto["Organske_Molekule"] == "Da")]
plt.scatter(df_kandidati["GPS_LONG"], df_kandidati["GPS_LAT"], marker="*", s=250, color="red")
plt.savefig("karta_kandidata.png", dpi=200)
plt.close()

plt.figure(figsize=(12, 8))
granice = [
    df_cisto["GPS_LONG"].min(),
    df_cisto["GPS_LONG"].max(),
    df_cisto["GPS_LAT"].min(),
    df_cisto["GPS_LAT"].max()
]
slika = plt.imread("jezero_crater_satellite_map.jpg")
plt.imshow(slika, extent=granice, aspect="auto", alpha=0.7)

sns.scatterplot(data=df_cisto, x="GPS_LONG", y="GPS_LAT", alpha=0.3, label="Uzorci")

plt.scatter(
    df_kandidati["GPS_LONG"],
    df_kandidati["GPS_LAT"],
    marker="*",
    s=250,
    color="yellow",
    zorder=5,
    label="Kandidati za bušenje"
)

plt.legend()
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Misijska karta - Jezero krater")

plt.savefig("misijska_karta_jezero.jpg", dpi=200)
plt.close()

lista = []
for _, red in df_kandidati.iterrows():
    lista.append({
        "ID_Uzorka": int(red["ID_Uzorka"]),
        "GPS_LAT": float(red["GPS_LAT"]),
        "GPS_LONG": float(red["GPS_LONG"]),
        "akcije": [
            {"tip": "NAVIGACIJA"},
            {"tip": "SONDIRANJE"},
            {"tip": "SLANJE_PODATAKA"}
        ]
    })

podatci = {"kandidati": lista}

with open("nexus_payload.json", "w", encoding="utf-8") as f:
    json.dump(podatci, f, ensure_ascii=False, indent=2)
