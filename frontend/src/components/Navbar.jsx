import { Link } from 'react-router-dom';

export default function Navbar() {
    return (
        <nav className="bg-white shadow-md sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo and Brand */}
                    <Link to="/" className="flex items-center space-x-2">
                        <div className="text-2xl">🏥</div>
                        <div>
                            <h1 className="text-xl font-bold text-primary-700">
                                Kenya Health Access
                            </h1>
                            <p className="text-xs text-gray-500">Find Healthcare Near You</p>
                        </div>
                    </Link>

                    {/* Navigation Links */}
                    <div className="hidden md:flex items-center space-x-6">
                        <Link
                            to="/"
                            className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                        >
                            Home
                        </Link>
                        <Link
                            to="/search"
                            className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                        >
                            Search Facilities
                        </Link>
                        <Link
                            to="/about"
                            className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                        >
                            About
                        </Link>
                        <Link
                            to="/manage"
                            className="text-primary-600 hover:text-primary-700 font-bold border border-primary-200 px-3 py-1 rounded-md bg-primary-50 transition-colors"
                        >
                            Manage
                        </Link>
                    </div>

                    {/* USSD Info */}
                    <div className="hidden lg:flex items-center space-x-2 bg-primary-50 px-4 py-2 rounded-lg">
                        <span className="text-sm font-medium text-primary-700">
                            📞 Dial *384# for USSD
                        </span>
                    </div>

                    {/* Mobile Menu Button */}
                    <button className="md:hidden p-2 rounded-lg hover:bg-gray-100">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                </div>
            </div>
        </nav>
    );
}
