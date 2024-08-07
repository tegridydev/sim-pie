from simulator import Simulator


def main():
    simulator = Simulator(1100, 600)  # 800x600 for simulation, 300x600 for GUI
    simulator.run()


if __name__ == "__main__":
    main()
