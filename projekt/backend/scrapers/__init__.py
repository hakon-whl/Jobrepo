"""
Scraper-Module für verschiedene Job-Plattformen.
"""

# Keine direkten Imports hier, da sie zu zirkulären Imports führen können
__all__ = ["RequestBaseScraper", "StepstoneScraper", "XingScraper", "SeleniumBaseScraper", "StellenanzeigenScraper"]


if __name__ == "__main__":
    import sys
    import traceback
    import time
    from typing import Dict, Any, List

    # Import der Config und Scraper-Klassen
    from projekt.backend.core.config import Site, get_site_config
    from projekt.backend.scrapers.stepstone_scraper import StepstoneScraper
    from projekt.backend.scrapers.xing_scraper import XingScraper
    from projekt.backend.scrapers.stellenanzeigen_scraper import StellenanzeigenScraper


    def get_test_search_criteria() -> Dict[str, Any]:
        """Liefert realistische Test-Suchkriterien"""
        return {
            "jobTitle": "Praktikant",
            "location": "München",
            "radius": "20",
            "discipline": "IT"
        }


    def test_scraper_configuration():
        """Testet die Scraper-Konfigurationen"""
        print("🔧 KONFIGURATION TESTING")
        print("-" * 40)

        for site_enum in Site:
            config = get_site_config(site_enum)
            if config:
                print(f"✅ {site_enum.value}: Konfiguration geladen")

                # Wichtige Config-Keys prüfen
                required_keys = ["base_url", "search_url_template"]
                missing_keys = [key for key in required_keys if not config.get(key)]

                if missing_keys:
                    print(f"   ⚠️ Fehlende Keys: {missing_keys}")
                else:
                    print(f"   ✅ Alle wichtigen Keys vorhanden")

                # Scraper-Typ identifizieren
                if "selenium_" in str(config):
                    print(f"   🤖 Scraper-Typ: Selenium-basiert")
                else:
                    print(f"   📡 Scraper-Typ: Request-basiert")

            else:
                print(f"❌ {site_enum.value}: Keine Konfiguration gefunden")
        print()


    def test_url_generation():
        """Testet die URL-Generierung für alle Sites"""
        print("🔗 URL-GENERIERUNG TESTING")
        print("-" * 40)

        test_criteria = get_test_search_criteria()

        scrapers = {
            Site.STEPSTONE: StepstoneScraper(),
            Site.XING: XingScraper(),
            Site.STELLENANZEIGEN: StellenanzeigenScraper()
        }

        for site_enum, scraper in scrapers.items():
            try:
                config = get_site_config(site_enum)
                template = config.get("search_url_template", "")

                # URL generieren
                search_url = scraper._construct_search_url(template, test_criteria)

                print(f"✅ {site_enum.value}:")
                print(f"   📋 Template: {template}")
                print(f"   🔗 URL: {search_url}")
                print()

            except Exception as e:
                print(f"❌ {site_enum.value}: Fehler bei URL-Generierung - {e}")
                print()


    def test_scraper_initialization():
        """Testet die Initialisierung aller Scraper"""
        print("🚀 SCRAPER INITIALISIERUNG TESTING")
        print("-" * 40)

        scraper_classes = {
            "StepStone": StepstoneScraper,
            "XING": XingScraper,
            "Stellenanzeigen": StellenanzeigenScraper
        }

        successful_init = []
        failed_init = []

        for name, scraper_class in scraper_classes.items():
            try:
                scraper = scraper_class()
                print(f"✅ {name}: Erfolgreich initialisiert")
                print(f"   📍 Base URL: {scraper.base_url}")
                print(f"   ⚙️ Config Keys: {list(scraper.config.keys())[:5]}...")
                successful_init.append(name)

                # Cleanup
                try:
                    scraper.close_client()
                except:
                    pass  # Ignore cleanup errors

            except Exception as e:
                print(f"❌ {name}: Initialisierung fehlgeschlagen - {e}")
                failed_init.append(name)

        print(f"\n📊 Ergebnis: {len(successful_init)}/{len(scraper_classes)} erfolgreich")
        print()


    def test_limited_scraping():
        """Führt begrenzte Scraping-Tests durch"""
        print("🕷️ BEGRENZTES SCRAPING TESTING")
        print("-" * 40)
        print("⚠️ Hinweis: Nur wenige URLs werden getestet um Rate-Limiting zu vermeiden")
        print()

        test_criteria = get_test_search_criteria()
        results = {}

        # Test-Konfiguration: Welche Scraper testen?
        scraper_tests = [
            ("StepStone", StepstoneScraper, "request_based"),
            ("XING", XingScraper, "selenium_based"),
            ("Stellenanzeigen", StellenanzeigenScraper, "selenium_based")
        ]

        for scraper_name, scraper_class, scraper_type in scraper_tests:
            print(f"🔍 Testing {scraper_name} ({scraper_type})...")

            scraper = None
            try:
                # Scraper initialisieren
                scraper = scraper_class()

                # Test 1: URL-Sammlung (mit angepasster Logik für jeden Scraper-Typ)
                print(f"   📋 Sammle URLs...")
                start_time = time.time()

                # ✅ ANGEPASSTE LOGIK FÜR ALLE SCRAPER
                if scraper_type == "request_based":
                    # StepStone: Request-basiert, schneller
                    job_urls = scraper.get_search_result_urls(test_criteria)
                    job_urls = job_urls[:3] if job_urls else []  # Max 3 URLs
                else:
                    # XING und Stellenanzeigen: Selenium-basiert, langsamer
                    job_urls = scraper.get_search_result_urls(test_criteria)
                    job_urls = job_urls[:2] if job_urls else []  # Max 2 URLs

                url_time = time.time() - start_time

                if job_urls:
                    print(f"   ✅ {len(job_urls)} URLs gefunden ({url_time:.1f}s)")

                    # Test 2: Detail-Extraktion (nur erste URL)
                    if job_urls:
                        print(f"   📄 Extrahiere Details vom ersten Job...")
                        detail_start = time.time()

                        details = scraper.extract_job_details(job_urls[0])
                        detail_time = time.time() - detail_start

                        if details:
                            title = details.get('title', 'Unbekannt')[:50]
                            raw_text_length = len(details.get('raw_text', ''))

                            print(f"   ✅ Details extrahiert ({detail_time:.1f}s)")
                            print(f"      💼 Titel: {title}...")
                            print(f"      📝 Text-Länge: {raw_text_length} Zeichen")

                            results[scraper_name] = {
                                "success": True,
                                "urls_found": len(job_urls),
                                "details_extracted": True,
                                "url_time": url_time,
                                "detail_time": detail_time,
                                "sample_title": title,
                                "scraper_type": scraper_type
                            }
                        else:
                            print(f"   ❌ Detail-Extraktion fehlgeschlagen")
                            results[scraper_name] = {
                                "success": False,
                                "urls_found": len(job_urls),
                                "details_extracted": False,
                                "error": "Detail extraction failed",
                                "scraper_type": scraper_type
                            }
                else:
                    print(f"   ❌ Keine URLs gefunden")
                    results[scraper_name] = {
                        "success": False,
                        "urls_found": 0,
                        "details_extracted": False,
                        "error": "No URLs found",
                        "scraper_type": scraper_type
                    }

            except Exception as e:
                print(f"   ❌ Fehler: {e}")
                results[scraper_name] = {
                    "success": False,
                    "error": str(e),
                    "scraper_type": scraper_type
                }

            finally:
                # Cleanup
                if scraper:
                    try:
                        scraper.close_client()
                        print(f"   🧹 Client geschlossen")
                    except Exception as cleanup_error:
                        print(f"   ⚠️ Cleanup-Fehler: {cleanup_error}")

            print()

        return results


    def print_test_summary(results: Dict[str, Any]):
        """Druckt eine Zusammenfassung der Test-Ergebnisse"""
        print("=" * 60)
        print("📊 TEST-ZUSAMMENFASSUNG")
        print("=" * 60)

        successful_scrapers = 0
        total_urls = 0
        total_time = 0
        selenium_scrapers = 0
        request_scrapers = 0

        for scraper_name, result in results.items():
            print(f"\n🔸 {scraper_name} ({result.get('scraper_type', 'unknown')}):")

            if result.get("success"):
                successful_scrapers += 1
                urls = result.get("urls_found", 0)
                total_urls += urls

                print(f"   ✅ Status: Erfolgreich")
                print(f"   📋 URLs: {urls}")
                print(f"   📄 Details: {'✅' if result.get('details_extracted') else '❌'}")

                if result.get("url_time"):
                    print(f"   ⏱️ URL-Zeit: {result['url_time']:.1f}s")
                    total_time += result['url_time']

                if result.get("detail_time"):
                    print(f"   ⏱️ Detail-Zeit: {result['detail_time']:.1f}s")
                    total_time += result['detail_time']

                if result.get("sample_title"):
                    print(f"   💼 Beispiel: {result['sample_title']}")

            else:
                print(f"   ❌ Status: Fehlgeschlagen")
                if result.get("error"):
                    print(f"   🚨 Fehler: {result['error']}")

            # Scraper-Typ zählen
            if result.get('scraper_type') == 'selenium_based':
                selenium_scrapers += 1
            elif result.get('scraper_type') == 'request_based':
                request_scrapers += 1

        print(f"\n🎯 GESAMT-STATISTIK:")
        print(f"   ✅ Erfolgreiche Scraper: {successful_scrapers}/{len(results)}")
        print(f"   📋 Gesamt URLs: {total_urls}")
        print(f"   ⏱️ Gesamt Zeit: {total_time:.1f}s")
        print(f"   🤖 Selenium-Scraper: {selenium_scrapers}")
        print(f"   📡 Request-Scraper: {request_scrapers}")

        success_rate = (successful_scrapers / len(results)) * 100 if results else 0
        print(f"   📈 Erfolgsrate: {success_rate:.1f}%")


    def run_full_test_suite():
        """Führt die vollständige Test-Suite aus"""
        print("🧪 SCRAPER MODULE - VOLLSTÄNDIGE TEST-SUITE")
        print("=" * 60)
        print(f"🎯 Teste {len(Site)} Job-Plattformen")
        print("=" * 60)
        print()

        # Test 1: Konfiguration
        test_scraper_configuration()

        # Test 2: URL-Generierung
        test_url_generation()

        # Test 3: Initialisierung
        test_scraper_initialization()

        # Test 4: Begrenztes Scraping
        results = test_limited_scraping()

        # Zusammenfassung
        print_test_summary(results)

        # Endergebnis
        successful_scrapers = sum(1 for r in results.values() if r.get("success"))
        if successful_scrapers > 0:
            print(f"\n🎉 Test-Suite erfolgreich abgeschlossen!")
            print(f"💡 Tipp: Verwende 'python -m projekt.backend.scrapers <scraper>' für Einzeltests")
        else:
            print(f"\n⚠️ Alle Tests fehlgeschlagen - Config oder Netzwerk prüfen!")


    def test_single_scraper(scraper_name: str):
        """Testet einen einzelnen Scraper intensiver"""
        scraper_map = {
            "stepstone": ("StepStone", StepstoneScraper),
            "xing": ("XING", XingScraper),
            "stellenanzeigen": ("Stellenanzeigen", StellenanzeigenScraper)
        }

        if scraper_name.lower() not in scraper_map:
            print(f"❌ Unbekannter Scraper: {scraper_name}")
            print(f"Verfügbare Scraper: {list(scraper_map.keys())}")
            return

        display_name, scraper_class = scraper_map[scraper_name.lower()]
        print(f"🔍 EINZELTEST: {display_name}")
        print("=" * 40)

        test_criteria = get_test_search_criteria()
        print(f"🎯 Test-Kriterien: {test_criteria}")
        print()

        scraper = None
        try:
            # Initialisierung
            print("🚀 Initialisiere Scraper...")
            scraper = scraper_class()
            config = scraper.config
            print(f"✅ Scraper bereit - Base URL: {scraper.base_url}")
            print(f"⚙️ Timeout: {config.get('timeout', 'N/A')}s")
            print(f"🔁 Max Retries: {config.get('max_retries', 'N/A')}")

            # Scraper-Typ erkennen
            scraper_type = "selenium_based" if hasattr(scraper, 'driver') else "request_based"
            print(f"🔧 Scraper-Typ: {scraper_type}")
            print()

            # URL-Sammlung
            print("📋 Sammle Job-URLs...")
            start_time = time.time()
            job_urls = scraper.get_search_result_urls(test_criteria)
            url_time = time.time() - start_time

            if job_urls:
                print(f"✅ {len(job_urls)} URLs gefunden in {url_time:.2f}s")
                print("📝 Erste 3 URLs:")
                for i, url in enumerate(job_urls[:3], 1):
                    print(f"   {i}. {url}")
                print()

                # Detail-Extraktion von ersten 2 Jobs
                max_details = 2 if scraper_type == "selenium_based" else 3
                for i, url in enumerate(job_urls[:max_details], 1):
                    print(f"📄 Extrahiere Details von Job {i}...")
                    detail_start = time.time()
                    details = scraper.extract_job_details(url)
                    detail_time = time.time() - detail_start

                    if details:
                        print(f"✅ Details extrahiert in {detail_time:.2f}s")
                        print(f"   💼 Titel: {details.get('title', 'N/A')}")
                        print(f"   🔗 URL: {details.get('url', 'N/A')}")
                        print(f"   📝 Text-Länge: {len(details.get('raw_text', ''))} Zeichen")

                        # Zeige ersten Teil des Textes für Stellenanzeigen
                        if scraper_name.lower() == "stellenanzeigen" and details.get('raw_text'):
                            preview = details['raw_text'][:200] + "..." if len(details['raw_text']) > 200 else details['raw_text']
                            print(f"   📖 Text-Vorschau: {preview}")
                        print()
                    else:
                        print(f"❌ Detail-Extraktion fehlgeschlagen")
                        print()
            else:
                print("❌ Keine URLs gefunden")

        except Exception as e:
            print(f"❌ Fehler beim Testen: {e}")
            traceback.print_exc()

        finally:
            if scraper:
                scraper.close_client()
                print("🧹 Cleanup abgeschlossen")


    # Hauptausführung
    try:
        if len(sys.argv) > 1:
            # Einzelner Scraper Test
            scraper_name = sys.argv[1]
            test_single_scraper(scraper_name)
        else:
            # Vollständige Test-Suite
            run_full_test_suite()

    except KeyboardInterrupt:
        print("\n\n⚠️ Test durch Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unerwarteter Fehler: {e}")
        traceback.print_exc()
        sys.exit(1)