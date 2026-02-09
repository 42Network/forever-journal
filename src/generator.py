class JournalGenerator:
    def __init__(self, user_data_path=None, profile_name="default_a4"):
        from .utils import load_user_data, get_profile
        self.user_data = load_user_data(user_data_path) if user_data_path else load_user_data()
        self.profile = get_profile(profile_name)

    def generate(self, output_path: str = "output"):
        print(f"Generating journal for {self.user_data.start_year}-{self.user_data.start_year + self.user_data.num_years - 1}")
        print(f"Using profile: {self.profile.description}")
        print(f"Paper: {self.profile.paper_size}, Margins: {self.profile.margins}")
        print(f"Events loaded: {len(self.user_data.special_days.birthdays)} birthdays")
        pass
