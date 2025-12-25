export default function About() {
    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">About Kenya Health Access</h1>
                    <p className="text-xl text-gray-600">
                        Connecting Kenyans to quality healthcare facilities nationwide
                    </p>
                </div>

                {/* Mission */}
                <div className="card mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Our Mission</h2>
                    <p className="text-gray-700 leading-relaxed">
                        Kenya Health Access is dedicated to improving healthcare accessibility across Kenya by providing
                        a comprehensive, easy to use platform for finding healthcare facilities. We believe that everyone
                        deserves access to quality healthcare information, regardless of their location or internet connectivity.
                    </p>
                </div>

                {/* Features */}
                <div className="card mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">What We Offer</h2>
                    <div className="space-y-4">
                        <div className="flex items-start space-x-4">
                            <div className="text-3xl">🔍</div>
                            <div>
                                <h3 className="font-bold text-gray-900 mb-1">Comprehensive Search</h3>
                                <p className="text-gray-700">
                                    Search thousands of healthcare facilities across all 47 counties in Kenya,
                                    including hospitals, clinics, pharmacies, and specialized care centers.
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start space-x-4">
                            <div className="text-3xl">📱</div>
                            <div>
                                <h3 className="font-bold text-gray-900 mb-1">USSD Access</h3>
                                <p className="text-gray-700">
                                    Access our platform via USSD (*384#) on any mobile phone, even without
                                    internet connection. Perfect for feature phones and areas with limited connectivity.
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start space-x-4">
                            <div className="text-3xl">✓</div>
                            <div>
                                <h3 className="font-bold text-gray-900 mb-1">Verified Information</h3>
                                <p className="text-gray-700">
                                    All facility information is regularly verified and updated to ensure accuracy.
                                    We provide details on services, NHIF acceptance, emergency availability, and more.
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start space-x-4">
                            <div className="text-3xl">🗺️</div>
                            <div>
                                <h3 className="font-bold text-gray-900 mb-1">Location-Based Search</h3>
                                <p className="text-gray-700">
                                    Find healthcare facilities near you using our interactive map and proximity search features.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* How to Use */}
                <div className="card mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">How to Use</h2>
                    <div className="space-y-6">
                        <div>
                            <h3 className="font-bold text-gray-900 mb-2">🌐 Web Platform</h3>
                            <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                                <li>Visit our website and use the search bar to find facilities</li>
                                <li>Filter by county, facility type, services, or NHIF acceptance</li>
                                <li>View detailed information about each facility</li>
                                <li>Get directions or call facilities directly from the platform</li>
                            </ol>
                        </div>

                        <div>
                            <h3 className="font-bold text-gray-900 mb-2">📱 USSD (*384#)</h3>
                            <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                                <li>Dial *384# from any mobile phone</li>
                                <li>Follow the menu prompts to search by county or facility type</li>
                                <li>Receive facility information via SMS</li>
                                <li>No internet connection required!</li>
                            </ol>
                        </div>
                    </div>
                </div>

                {/* Contact */}
                <div className="card bg-gradient-to-r from-primary-50 to-secondary-50">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Get in Touch</h2>
                    <p className="text-gray-700 mb-4">
                        Have questions, suggestions, or want to add your facility to our platform?
                        We'd love to hear from you!
                    </p>
                    <div className="space-y-2">
                        <p className="text-gray-700">
                            <span className="font-medium">USSD:</span> Dial *384#
                        </p>
                        <p className="text-gray-700">
                            <span className="font-medium">Email:</span> info@kenyahealthaccess.ke
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
