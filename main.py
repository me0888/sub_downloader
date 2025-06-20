
import yt_dlp
import os
import sys

def download_subtitles(video_url, language='ru', output_dir='subtitles'):
    """
    Скачивает субтитры с YouTube видео
    
    Args:
        video_url (str): URL YouTube видео
        language (str): Код языка субтитров (по умолчанию 'ru')
        output_dir (str): Папка для сохранения субтитров
    """
    # Создаем папку для субтитров если её нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Настройки для yt-dlp
    ydl_opts = {
        'writesubtitles': True,        # Скачивать субтитры
        'writeautomaticsub': True,     # Скачивать автоматические субтитры если обычных нет
        'subtitleslangs': [language],  # Язык субтитров
        'skip_download': True,         # Не скачивать видео, только субтитры
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',  # Шаблон имени файла
        'subtitlesformat': 'srt',      # Формат субтитров
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Получаем информацию о видео
            info = ydl.extract_info(video_url, download=False)
            video_title = info.get('title', 'Unknown')
            
            print(f"Видео: {video_title}")
            print(f"Скачиваем субтитры на языке: {language}")
            
            # Скачиваем субтитры
            ydl.download([video_url])
            
            print(f"✅ Субтитры успешно скачаны в папку '{output_dir}'")
            
    except Exception as e:
        print(f"❌ Ошибка при скачивании субтитров: {str(e)}")

def list_available_subtitles(video_url):
    """
    Показывает доступные языки субтитров для видео
    """
    ydl_opts = {
        'listsubtitles': True,
        'skip_download': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            print(f"\nВидео: {info.get('title', 'Unknown')}")
            print("\nДоступные субтитры:")
            
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            if subtitles:
                print("Обычные субтитры:")
                for lang in subtitles.keys():
                    print(f"  - {lang}")
            
            if automatic_captions:
                print("Автоматические субтитры:")
                for lang in automatic_captions.keys():
                    print(f"  - {lang}")
                    
            if not subtitles and not automatic_captions:
                print("  Субтитры не найдены")
                
    except Exception as e:
        print(f"❌ Ошибка при получении информации: {str(e)}")

def main():
    print("🎬 YouTube Subtitle Downloader")
    print("=" * 40)
    
    while True:
        print("\nВыберите действие:")
        print("1. Скачать субтитры")
        print("2. Показать доступные языки субтитров")
        print("3. Выход")
        
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == '1':
            video_url = input("Введите URL YouTube видео: ").strip()
            if not video_url:
                print("❌ URL не может быть пустым")
                continue
                
            language = input("Введите код языка (например, ru, en, es) [по умолчанию: ru]: ").strip()
            if not language:
                language = 'ru'
                
            download_subtitles(video_url, language)
            
        elif choice == '2':
            video_url = input("Введите URL YouTube видео: ").strip()
            if not video_url:
                print("❌ URL не может быть пустым")
                continue
                
            list_available_subtitles(video_url)
            
        elif choice == '3':
            print("👋 До свидания!")
            break
            
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
