export default function Footer() {
  return (
    <footer className="w-full bg-[#013172] text-white py-4 px-6">
      <div className="flex flex-col md:flex-row items-center justify-between w-full text-sm">
        {/* Left corner */}
        <p className="md:text-left w-full md:w-auto">
          stop reacting to demand. start predicting it.
        </p>

        {/* Center */}
        <p className="text-center w-full md:w-auto">
          © 2025 foresight. All rights reserved.
        </p>

        {/* Right corner */}
        <div className="flex space-x-6 mt-2 md:mt-0 w-full md:w-auto justify-center md:justify-end">
          <a href="/about" className="hover:underline">
            About
          </a>
          <a href="/contact" className="hover:underline">
            Contact
          </a>
        </div>
      </div>
    </footer>
  );
}
