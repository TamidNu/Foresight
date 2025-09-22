

export default function Footer() {
    return (
      <footer className="w-full bg-[#013172] text-white py-4 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between text-sm">
          <p>© 2025 foresight. All rights reserved.</p>
          <div className="flex space-x-6 mt-2 md:mt-0">
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
  
