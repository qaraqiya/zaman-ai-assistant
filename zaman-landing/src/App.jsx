import { motion } from "framer-motion";
import { useEffect, useState } from "react";

/* ---------- Floating Glass Navbar ---------- */
const Navbar = () => {
    const items = [
        { id: "hero", label: "главная" },
        { id: "sabina", label: "sabina.csv" },
        { id: "abu", label: "abu" },
        { id: "extra", label: "extra" },
    ];

    const [open, setOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const [active, setActive] = useState("hero");

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 10);
        window.addEventListener("scroll", onScroll, { passive: true });
        return () => window.removeEventListener("scroll", onScroll);
    }, []);

    useEffect(() => {
        const sections = items
            .map((i) => document.getElementById(i.id))
            .filter(Boolean);
        const io = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) setActive(entry.target.id);
                });
            },
            { rootMargin: "-40% 0px -50% 0px", threshold: 0.1 }
        );
        sections.forEach((s) => io.observe(s));
        return () => io.disconnect();
    }, []);

    const handleJump = (e, id) => {
        e.preventDefault();
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
        setOpen(false);
    };

    return (
        <div className="fixed top-3 left-1/2 -translate-x-1/2 z-50 w-full px-3 md:px-6 pointer-events-none">
            <nav
                className={[
                    "mx-auto max-w-6xl pointer-events-auto",
                    "rounded-full border backdrop-blur-xl transition-all duration-300",
                    scrolled
                        ? "bg-white/80 border-[#2D9A86]/30 shadow-xl"
                        : "bg-white/60 border-white/20 shadow-md",
                ].join(" ")}>
                <div className="flex items-center justify-between px-5 md:px-8 py-3 md:py-3.5">
                    <a
                        href="#hero"
                        onClick={(e) => handleJump(e, "hero")}
                        className="text-lg font-semibold tracking-tight text-[#2D9A86]">
                        Zaman AI
                    </a>

                    <ul className="hidden md:flex items-center gap-2">
                        {items.map((it) => (
                            <li key={it.id}>
                                <a
                                    href={`#${it.id}`}
                                    onClick={(e) => handleJump(e, it.id)}
                                    className={[
                                        "px-4 py-2 rounded-full transition-all duration-200",
                                        active === it.id
                                            ? "bg-[#2D9A86] text-white"
                                            : "text-gray-700 hover:bg-[#2D9A86]/10",
                                    ].join(" ")}>
                                    {it.label}
                                </a>
                            </li>
                        ))}
                    </ul>

                    <button
                        className="md:hidden text-2xl"
                        onClick={() => setOpen((s) => !s)}
                        aria-label="Toggle menu">
                        ☰
                    </button>
                </div>

                {open && (
                    <div className="md:hidden px-3 pb-3">
                        <ul className="grid gap-2">
                            {items.map((it) => (
                                <li key={it.id}>
                                    <a
                                        href={`#${it.id}`}
                                        onClick={(e) => handleJump(e, it.id)}
                                        className={[
                                            "block w-full px-4 py-2 rounded-xl text-center",
                                            active === it.id
                                                ? "bg-[#2D9A86] text-white"
                                                : "text-gray-700 bg-white/70 hover:bg-[#2D9A86]/10",
                                        ].join(" ")}>
                                        {it.label}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </nav>
        </div>
    );
};

/* ---------- Reusable Section Component ---------- */
const Section = ({ id, title, children, gradient }) => (
    <motion.section
        id={id}
        className={`relative min-h-screen flex flex-col items-center justify-center text-center px-6 py-24 md:py-28 overflow-hidden scroll-mt-28 ${gradient}`}
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        viewport={{ once: true }}>
        <div className="absolute inset-0 -z-10 blur-[120px] opacity-50 bg-gradient-to-tr from-[#EEFE6D] via-white to-[#2D9A86]"></div>
        <div className="absolute inset-0 -z-20 bg-white/40 backdrop-blur-3xl"></div>

        {title && (
            <motion.h2
                className="text-5xl font-bold mb-6 bg-gradient-to-r from-[#2D9A86] via-[#48C5B0] to-[#EEFE6D] bg-clip-text text-transparent"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}>
                {title}
            </motion.h2>
        )}

        <motion.div
            className="max-w-3xl text-gray-700 text-lg leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}>
            {children}
        </motion.div>
    </motion.section>
);

/* ---------- App (Main Page) ---------- */
export default function App() {
    return (
        <div className="font-sans text-gray-900 bg-white">
            <Navbar />

            <Section
                id="hero"
                gradient="bg-gradient-to-br from-[#EEFE6D] via-white to-[#2D9A86]/10">
                <div className="relative pt-32 pb-10 flex flex-col items-center justify-center">
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 2 }}
                        className="absolute -top-40 w-[600px] h-[600px] bg-gradient-to-tr from-[#EEFE6D] via-[#A8F1DC] to-[#2D9A86] rounded-full blur-[150px] opacity-70"></motion.div>

                    {/* Replaced Shield with Iris */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3, duration: 1 }}
                        className="relative z-10 w-80 h-80 md:w-96 md:h-96 flex items-center justify-center rounded-[3rem] border border-white/30 bg-white/30 backdrop-blur-3xl shadow-[0_0_40px_rgba(45,154,134,0.3)]">
                        <h1 className="text-6xl font-extrabold bg-gradient-to-r from-[#2D9A86] via-[#48C5B0] to-[#EEFE6D] bg-clip-text text-transparent">
                            Iris
                        </h1>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 50 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6, duration: 1 }}
                        className="relative z-20 text-center mt-12">
                        <h1 className="text-6xl font-extrabold mb-6 bg-gradient-to-r from-[#2D9A86] via-[#48C5B0] to-[#EEFE6D] bg-clip-text text-transparent">
                            Финансовый ассистент Iris
                        </h1>
                        <p className="text-lg text-gray-700 mb-8 max-w-2xl mx-auto">
                            Проект команды <b>Sabina.csv</b> — умный помощник,
                            который помогает вам осознанно управлять деньгами,
                            без стресса и лишней информации 💚
                        </p>
                        <a
                            href="#abu"
                            className="bg-[#2D9A86] text-white px-8 py-3 rounded-full text-lg shadow-lg hover:bg-[#238E79] transition">
                            Познакомиться с Iris ↓
                        </a>
                    </motion.div>
                </div>
            </Section>
            {/* Sabinia.csv */}
            <Section
                id="sabina"
                title="Команда Sabina.csv"
                gradient="bg-gradient-to-br from-white via-[#EEFE6D]/30 to-[#2D9A86]/10">
                <p>
                    Мы — команда студентов из SDU University. Нас питают
                    интересные люди, сложные задачки, и мемы.
                </p>
                <div className="grid md:grid-cols-3 gap-6 mt-10"></div>
            </Section>
            {/* Abu */}
            <section
                id="abu"
                className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#EEFE6D]/40 to-[#2D9A86]/10 py-20">
                <h2 className="text-4xl font-bold text-[#2D9A86] mb-6">
                    Abu — AI Assistant (Streamlit)
                </h2>
                <p className="text-gray-700 mb-6 text-center max-w-xl">
                    Это ваш обученный ассистент. Задавайте вопросы — Abu ответит
                    на основе модели Sabinia.csv.
                </p>
                <div className="w-full max-w-5xl h-[800px] rounded-3xl overflow-hidden shadow-[0_0_40px_rgba(45,154,134,0.15)] border border-[#2D9A86]/20">
                    <iframe
                        src="http://localhost:8501"
                        width="100%"
                        height="100%"
                        className="rounded-3xl border-none"
                    />
                </div>
            </section>
            {/* Extra */}
            <Section
                id="extra"
                title="Extra 💫"
                gradient="bg-gradient-to-tr from-white via-[#EEFE6D]/40 to-[#2D9A86]/10">
                <div className="grid md:grid-cols-3 gap-6 mt-10">
                    {[
                        {
                            emoji: "🔔",
                            title: "Пуш-уведомления",
                            text: "Iris мягко напоминает о целях, платежах и финансовом здоровье.",
                        },
                        {
                            emoji: "🔥",
                            title: "Стрики",
                            text: "Следи за сериями успеха — ежедневные мини-достижения мотивируют!",
                        },
                        {
                            emoji: "💬",
                            title: "Советы и инсайты",
                            text: "AI-подсказки о привычках, инвестициях и халяль-финансах в твоем ритме.",
                        },
                        {
                            emoji: "🎯",
                            title: "Финансовые цели",
                            text: "Создавай цели — например, хадж, обучение или жильё — и Iris покажет путь.",
                        },
                        {
                            emoji: "🌙",
                            title: "Мягкий ночной режим",
                            text: "Спокойные цвета, адаптированные под настроение и фокус.",
                        },
                        {
                            emoji: "💎",
                            title: "Персональные рекомендации",
                            text: "Iris обучается на твоих предпочтениях, предлагая только нужное.",
                        },
                    ].map((f, i) => (
                        <motion.div
                            key={i}
                            whileHover={{ scale: 1.05 }}
                            className="p-8 bg-white/70 rounded-3xl shadow-lg backdrop-blur-lg border border-[#2D9A86]/20 text-center">
                            <div className="text-4xl mb-3">{f.emoji}</div>
                            <h3 className="text-xl font-semibold mb-2 text-[#2D9A86]">
                                {f.title}
                            </h3>
                            <p className="text-gray-600">{f.text}</p>
                        </motion.div>
                    ))}
                </div>
            </Section>
            {/* Footer */}
            <footer className="py-8 text-center text-gray-500 text-sm bg-white border-t border-[#2D9A86]/10">
                © 2025 Sabina.csv — Hackathon Zamanbank Project
            </footer>
        </div>
    );
}
