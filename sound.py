from gtts import gTTS

# Kalimat alarm
kalimat = "Peringatan! Deteksi objek mencurigakan berupa senjata api. Segera lakukan tindakan pengamanan."


# Bahasa Indonesia
tts = gTTS(text=kalimat, lang='id')

# Simpan ke file MP3
tts.save("peringatan_senja.mp3")

print("File suara berhasil dibuat: peringatan_senja.mp3")
