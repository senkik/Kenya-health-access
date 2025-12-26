import { Link } from 'react-router-dom';

export default function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-gray-800 text-white mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* About Section */}
                    <div>
                        <h3 className="text-lg font-bold mb-4">Kenya Health Access</h3>
                        <p className="text-gray-300 text-sm">
                            Connecting Kenyans to quality healthcare facilities across the country.
                            Find hospitals, clinics, and pharmacies near you.
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h3 className="text-lg font-bold mb-4">Quick Links</h3>
                        <ul className="space-y-2">
                            <li>
                                <Link to="/" className="text-gray-300 hover:text-white text-sm transition-colors">
                                    Home
                                </Link>
                            </li>
                            <li>
                                <Link to="/search" className="text-gray-300 hover:text-white text-sm transition-colors">
                                    Search Facilities
                                </Link>
                            </li>
                            <li>
                                <Link to="/about" className="text-gray-300 hover:text-white text-sm transition-colors">
                                    About Us
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Contact & USSD */}
                    <div>
                        <h3 className="text-lg font-bold mb-4">Access Healthcare</h3>
                        <div className="space-y-3">
                            <div className="bg-primary-600 px-4 py-3 rounded-lg">
                                <p className="text-sm font-medium">USSD Access (No Internet Required)</p>
                                <p className="text-2xl font-bold mt-1">*384*43149#</p>
                            </div>
                            <p className="text-gray-300 text-sm">
                                Works on all phones, including feature phones
                            </p>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="border-t border-gray-700 mt-8 pt-8 text-center">
                    <p className="text-gray-400 text-sm">
                        © {currentYear} Kenya Health Access. All rights reserved.
                    </p>
                </div>
            </div>
        </footer>
    );
}
